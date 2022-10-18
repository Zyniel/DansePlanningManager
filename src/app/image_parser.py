#!/usr/bin/python
# coding: utf-8
import logging
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
import json
from typing import Any
from PIL import Image
from pytesseract import pytesseract
from pytesseract import Output
from csv import Dialect
import cv2
import csv
import re
import dateparser
import image_utils
from babel.dates import format_date
from babel.dates import format_datetime
from babel.dates import format_time

DATE_LOCALE = "fr_FR"


class CsvTextBuilder(object):
    def __init__(self):
        self.csv_string = []

    def write(self, row):
        self.csv_string.append(row)


class CSVStandardDialect(Dialect):
    delimiter = ";"
    doublequote = True
    lineterminator = "\r\n"
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL


class Event(ABC):
    def __init__(self, start_date: datetime, description: str = "", end_date: datetime = None, location: str = ""):
        self.start_date = start_date
        self.end_date = end_date
        self.day = format_date(self.start_date, "eeee", locale=DATE_LOCALE).capitalize()
        self.description = description
        self.location = location

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def toJSON(self):
        pass

    @abstractmethod
    def short_infos():
        pass


class DanceEvent(Event):

    DATE_TEXT_FORMAT = "dd/MM/yyyy"
    TIME_TEXT_FORMAT = "HH:mm"

    def __init__(
        self, start_date: datetime, description: str = "", end_date: datetime = None, location: str = "", dances=[], raw = str
    ):
        super().__init__(start_date=start_date, description=description, end_date=end_date, location=location)
        self.dances = dances
        self.raw = raw

    def to_json_storage(self):
        return {
            "day": self.day,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "description": self.description,
            "location": self.location,
            "dances": self.dances,
            "raw" : json.dumps(self.raw)
        }
    def __iter__(self):
        hours = format_time(self.start_date, self.TIME_TEXT_FORMAT, locale=DATE_LOCALE)
        start_date = format_date(self.start_date, format=self.DATE_TEXT_FORMAT, locale=DATE_LOCALE)
        end_date = ""

        if not self.end_date is None:
            hours = hours + "-" + format_time(self.end_date, self.TIME_TEXT_FORMAT, locale=DATE_LOCALE)
            end_date = format_date(self.end_date, format=self.DATE_TEXT_FORMAT, locale=DATE_LOCALE)

        yield from {
            "day": self.day,
            "start_date": start_date,
            "end_date": end_date,
            "hours": hours,
            "description": self.description,
            "location": self.location,
            "dances": self.dances,
        }.items()

    def __str__(self):
        return json.dumps(dict(self), ensure_ascii=False, indent=0)

    def __repr__(self):
        return self.__str__()

    def toJSON(self):
        return self.__str__(self)

    def short_infos(self):
        desc = '{0} {1}-{2} | {3}'.format(
            format_date(self.start_date, 'dd/MM/yyyy', locale=DATE_LOCALE),
            format_time(self.start_date, 'HH:mm', locale=DATE_LOCALE),
            format_time(self.end_date, 'HH:mm', locale=DATE_LOCALE),
            self.description)
        return desc

class Planning(ABC):
    events = []

    def __init__(self):
        pass

    def add(self, event: Event):
        if type(event) is list:
            for e in event:
                self.add(e)
        elif isinstance(event, Event):
            try:
                idx = self.events.index(event)
                logging.warning("Event already exists !")
            except Exception as e:
                self.events.append(event)

    def remove(self, event: Event):
        if type(event) is list:
            for e in event:
                self.remove(e)
        elif isinstance(event, Event):
            try:
                if self.events.find(event) > 0:
                    self.events.remove(event)
                    self.remove(event)
            except Exception as e:
                logging.warning("Could not find event to remove !")

    def clear(self, event: Event):
        self.events.clear()

    def count(self):
        return len(self.events)

    @abstractmethod
    def toJSON(self) -> json:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __repr__(self):
        pass


class DancePlanning(Planning):
    events = []

    def __init__(self):
        super().__init__()

    def toJSON(self) -> json:
        logging.info()

    def __str__(self) -> str:
        return json.dumps(dict(self.events), ensure_ascii=False)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        yield from {"events": self.events}.items()


class PlanningParser(ABC):
    def __init__(self, planning: Planning):
        self.__planning = planning

    @property
    def planning(self):
        return self.__planning

    @abstractmethod
    def parse_data(self, details):
        pass

    @abstractmethod
    def ocr(self, image):
        pass

    @abstractmethod
    def prepare(self, image):
        pass

    @abstractmethod
    def write_to_csv(self, data, path):
        pass

    def process(self, image, path):
        image = self.prepare(image)
        details = self.ocr(image)
        if not (details is None):
            events = self.parse_data(details)
            self.planning.add(events)
            logging.info(">> Added Events: " + str(len(events)))
        logging.info(">> Total Events: " + str(self.planning.count()))


class DancePlanningParser(PlanningParser):
    planning = DancePlanning()

    def __init__(self, path_to_tesseract):
        super().__init__(self.planning)

        self.path_to_tesseract = path_to_tesseract
        # configure Tesseract
        # point tessaract_cmd to tessaract.exe
        pytesseract.tesseract_cmd = path_to_tesseract

    def process(self, image, path):
        super().process(image, path)

    def parse_data(self, details):
        events = []
        try:
            # convert words to lines
            parse_text = []
            word_list = []
            last_word = ""
            for word in details["text"]:
                # non empty strings are considered valid words
                if word != "":
                    word_list.append(word)
                    last_word = word
                # a sentence ends when current word is empty and previous wasn't
                if last_word != "" and word == "":
                    parse_text.append(word_list)
                    word_list = []

            # parse lines one by one
            data = []
            for line in parse_text:
                start_date = None
                end_date = None
                start_time = None
                end_time = None
                description = ""
                pos = 0

                # word type depends on its position
                # post-Process words and apply transformations if needed before storing into array
                for word in line:

                    # first word is the litteral day
                    if pos == 0:
                        day = word
                    elif pos == 1:
                        # fix potential typos
                        word = word.replace("S", "5") \
                                   .replace("I", "1") \
                                   .replace("O", "0") \
                                   .replace("§", "5") \
                                   .replace("T", "7")
                        start_date = word
                        # parse french date and format as dd/mm/yyyy
                    elif pos == 2:
                        # depending if time has start/end hours, split the word to isolate both and format as HH24:MI
                        word = word.replace("S", "5") \
                                   .replace("I", "1") \
                                   .replace("O", "0") \
                                   .replace("§", "5") \
                                   .replace("T", "7")
                        word = word.replace("h", ":")  # fix time format
                        word = word.replace("24:00", "00:00")  # fix hours
                        minus_pos = word.find("-")
                        if minus_pos != -1:
                            time_parts = word.split("-")
                            start_time = time_parts[0]
                            end_time = time_parts[1]
                        else:
                            start_time = word
                            end_time = "00:00"
                    else:
                        # fix weird words
                        if word.lower() == "wes":
                            word = "WCS"
                        elif word.lower() == "dj":
                            word = "DJ"
                        elif word.lower() == "sbk":
                            word = "SBK"

                        # fix typographical quotes - don't need that crap
                        word = word.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
                        word = word.replace("I'", "L'")  # fix I' => L'
                        word = word.replace("lmpasse", "Impasse")                        

                        # fix uncapitalized consonant + apostrophe
                        regexp = re.compile(r'^([a-zA-Z]\').*')
                        if regexp.search(word):
                            word = word[0:2].upper() + word[2:]

                        # fix missing initial consonant before apostrophe => guesss L
                        # if word starts by apostrophe and a vowel, add an L, else remove the '
                        if description == "":
                            if word[0:1] == "'":
                                regexp = re.compile(r'^\'[aeiouyAEIOUY\u00C0-\u017F]+.*')
                                if regexp.search(word):
                                    word = "L" + word
                                else:
                                    word = word.lstrip("'")

                        # titlecase if all lower
                        if word.lower() == word:
                            word = word.title()
                        # append all remaining words
                        if description == "":
                            description = word
                        else:
                            description += " " + word
                    pos = pos + 1

                # create Event from extracted data
                try:
                    event = DancePlanningParser.parse_event(day, start_date, start_time, end_time, description, line)
                    events.append(event)
                except Exception as e:
                    logging.error("Failed to generate event from raw data !")
                    raise e

        except Exception as e:
            logging.info(e)
            logging.info("Could not parse image.")

        finally:
            return events

    def write_to_csv(self, data, path):
        # write to CSV
        header = ["day", "date", "start_time", "end_time", "event"]

        csv.register_dialect("CSVStandardDialect", CSVStandardDialect)

        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write("\ufeff")
            writer = csv.writer(f, dialect="CSVStandardDialect")
            # write the header
            writer.writerow(header)
            # write multiple rows
            writer.writerows(data)

    def ocr(self, image):
        # configuring parameters for tesseract
        custom_config = r"-l eng+fre --oem 3 --psm 6"

        # extract text from image to a json structure
        # text = pytesseract.image_to_string(image)
        details = pytesseract.image_to_data(image, output_type=Output.DICT, config=custom_config)
        return details

    def prepare(self, image):
        source = image.copy()

        # increase image size to get a better number of pixels per characters
        image = image_utils.image_resize(image, width=2000)
        resized = image.copy()

        # Perform transformations on image to enhance OCR
        # converting image into gray scale image
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        grayed = image.copy()

        # Converting it to binary image by Thresholding
        # this step is require if you have colored image because if you skip this part
        # then tesseract won't able to detect text correctly and this will give incorrect result
        # image = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)[1]
        threshold = image.copy()

        # display image
        # cv2.imshow('threshold image', source)
        # cv2.imshow('threshold image', resized)
        # cv2.imshow('threshold image', grayed)
        # cv2.imshow('threshold image', threshold)
        # Maintain output window until user presses a key
        # cv2.waitKey(0)
        # Destroying present windows on screen
        # cv2.destroyAllWindows()
        return image

    @staticmethod
    def parse_event(
        day: str, start_date: str, start_time: str, end_time: str, description: str, raw : Any) -> DanceEvent:
        # leave day - discarded for now
        day = day

        # leave day - discarded for now
        description = description
        parser_settings = {'TIMEZONE': 'Europe/Paris', 'RETURN_AS_TIMEZONE_AWARE': True}
        # format start date
        start_date = dateparser.parse(start_date, languages=["fr"], settings=parser_settings)
        end_date = start_date

        # create single datetime from date and time
        start_time = dateparser.parse(start_time, languages=["fr"], settings=parser_settings)
        start_time = start_time.timetz()
        start_datetime = start_date
        start_datetime = datetime.combine(start_date, start_time)

        # create single datetime from date and time
        end_time = dateparser.parse(end_time, languages=["fr"], settings=parser_settings)
        end_time = end_time.timetz()
        # adjust end_date to the next day when end_date is earlier than start_time
        if start_time.hour > end_time.hour:
            end_date = start_date + timedelta(days=1)
        end_datetime = end_date
        end_datetime = datetime.combine(end_date, end_time)

        event = DanceEvent(
            start_date=start_datetime, end_date=end_datetime, description=description, location="", dances=[], raw = raw
        )

        return event
