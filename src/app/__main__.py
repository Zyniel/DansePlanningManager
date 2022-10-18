#!/usr/bin/python
# coding: utf-8

import os
import logging

# facebook scrapper
from facebook_scrapper import FacebookScrapper

# image parser
import image_utils
import utils
from image_parser import DancePlanningParser

# configuration
from configuration import Config
from configuration import (
    AppGlobalConfig,
    AppParserConfig,
    AppScrapperConfig,
    MongoConfig,
    GoogleServiceConfig,
    MicrosoftServiceConfig,
    WhatsappServiceConfig,
)
from dotenv import load_dotenv

# database storage
from db import MongoDB_Python

# calendar management / cloud calendars
import google_services
import msgraph_services
from calendar_manager import CalendarManager, GoogleCalendarManager, MicrosoftCalendarManager
from storage_manager import StorageManager, GoogleStorageManager, MicrosoftStorageManager

# notifiers
from whatsapp_bot import WhatsappBot

def main():

    DEBUG_LOGS = "debug.log"
    ALL_LOGS = "app.log"

    logging.basicConfig(level=logging.INFO)

    # load environment variables
    try:
        logging.debug("Loading environment variables file...")
        load_dotenv()
    except Exception as e:
        logging.error("Failed loading environment variables !")
        raise e

    # load config file
    try:
        logging.debug("Loading configuration file...")
        config_yaml = Config.load("./config/settings.yml")

        app_config = AppGlobalConfig(config_yaml)
        scrapper_config = AppScrapperConfig(config_yaml)
        parser_config = AppParserConfig(config_yaml)
        mongo_conf = MongoConfig(config_yaml)
        microsoft_services_config = MicrosoftServiceConfig(config_yaml)
        google_services_config = GoogleServiceConfig(config_yaml)
        whatsapp_services_config = WhatsappServiceConfig(config_yaml)

    except Exception as e:
        logging.error("Failed loading configuration !")
        raise e

    # folder properties
    logging.debug("Retrieving configuration")
    FOLDER_OUTPUT = parser_config.output_folder
    FOLDER_IMAGES_DOWNLOADED = os.path.join(FOLDER_OUTPUT, parser_config.download_folder)
    FOLDER_IMAGE_MATCHED_LOW = os.path.join(FOLDER_OUTPUT, parser_config.low_match_folder)
    FOLDER_IMAGE_MATCHED_MED = os.path.join(FOLDER_OUTPUT, parser_config.med_match_folder)
    FOLDER_IMAGE_MATCHED_TOP = os.path.join(FOLDER_OUTPUT, parser_config.top_match_folder)

    # facebook scrapper properties
    TARGET_PAGES = scrapper_config.pages
    SEARCH_DEPTH = scrapper_config.search_depth
    SAFETY_DELAY = scrapper_config.safety_delay
    EMAIL = scrapper_config.username
    PASSWORD = scrapper_config.password

    # image scrapper properties
    TESSERACT_EXE = r"{}".format(parser_config.executable)
    IMAGE_MATCH_TOP = parser_config.top_match
    IMAGE_MATCH_MID = parser_config.med_match
    DETECT_LOWER_HSV = parser_config.detection_lower_hsv
    DETECT_UPPER_HSV = parser_config.detection_upper_hsv

    # data storage
    MONGODB_PORT = mongo_conf.port
    MONGODB_HOSTNAME = mongo_conf.host
    MONGODB_DATABASE = mongo_conf.db_name
    MONGODB_USERNAME = mongo_conf.username
    MONGODB_PASSWORD = mongo_conf.password

    # Office API Services
    MS_CLIENT_ID = microsoft_services_config.client_id
    MS_SECRET_ID = microsoft_services_config.secret_id
    MS_CALENDAR_ENABLED = microsoft_services_config.calendar_enabled
    MS_STORAGE_ENABLED = microsoft_services_config.storage_enabled
    MS_STORAGE_FOLDER_LOW = microsoft_services_config.storage_folder_low
    MS_STORAGE_FOLDER_MED = microsoft_services_config.storage_folder_med
    MS_STORAGE_FOLDER_TOP = microsoft_services_config.storage_folder_top
    GOOGLE_CLIENT_ID = google_services_config.client_id
    GOOGLE_SECRET_ID = google_services_config.secret_id
    GOOGLE_CALENDAR_ENABLED = google_services_config.calendar_enabled
    GOOGLE_STORAGE_ENABLED = google_services_config.storage_enabled
    MS_STORAGE_FOLDER_LOW = google_services_config.storage_folder_low
    MS_STORAGE_FOLDER_MED = google_services_config.storage_folder_med
    MS_STORAGE_FOLDER_TOP = google_services_config.storage_folder_top    

    # Whatsapp Bot
    WHATSAPP_USER_DIR_FOLDER = whatsapp_services_config.user_dir_folder
    WHATSAPP_ENABLED = whatsapp_services_config.enabled

    # DEBUGGING
    # processing
    RUN_FACEBOOK_SCRAPPER = True
    RUN_IMAGE_FILTERING = True
    RUN_IMAGE_STORAGE = True
    RUN_IMAGE_PARSING = True    
    RUN_DATA_STORAGE = True
    RUN_ONLINE_CALENDAR_GOOGLE = False
    RUN_ONLINE_CALENDAR_MS = False
    RUN_WHATSAPP_NOTIFIER = False
    FORCE_CANDIDATE = False

    scrapper = None
    parser = None
    images_top = {}
    images_med = {}
    images_low = {}

    if RUN_FACEBOOK_SCRAPPER:
        # empty input/output folder
        utils.empty_folder(FOLDER_OUTPUT)

        # start facebook session
        logging.info("================= SCRAPPING FB =================")

        scrapper = FacebookScrapper(
            ids=TARGET_PAGES,
            folder=FOLDER_IMAGES_DOWNLOADED,
            depth=SEARCH_DEPTH,
            delay=SAFETY_DELAY,
            lowres=False,
            highres=True,
        )
        scrapper.login(EMAIL, PASSWORD)
        # #
        try:
            # access profiles
            logging.info("Scrapping Facebook Danse Plannings...")
            scrapper.collect(typ="pages")

            logging.info("================= GET IMAGES ===================")
            logging.info("Saving images locally")
            scrapper.download()

        finally:
            scrapper.close_and_quit()
    else:
        logging.debug("Skipped Facebook Scrapping !")

    if RUN_IMAGE_FILTERING:
        logging.info("================= FIND MATCHES =================")
        # Define path to tessaract.exe
        path_to_tesseract = TESSERACT_EXE

        # define color to search for
        lower_hsv = image_utils.to_np_array(DETECT_LOWER_HSV[0], DETECT_LOWER_HSV[1], DETECT_LOWER_HSV[2])
        upper_hsv = image_utils.to_np_array(DETECT_UPPER_HSV[0], DETECT_UPPER_HSV[1], DETECT_UPPER_HSV[2])

        # retrieve images in output_folder, identify potential candidates
        files = os.listdir(FOLDER_IMAGES_DOWNLOADED)
        logging.info("Found " + str(len(files)) + " files to analyze.")
        for filename in files:
            filepath = os.path.join(FOLDER_IMAGES_DOWNLOADED, filename)

            if os.path.isfile(filepath):
                # load image from file and compute match possibility
                image = image_utils.load_image(filepath)
                presence = image_utils.get_color_presence(image, lower_hsv, upper_hsv)

                # depending on similarity process or skip files
                # then store in folders depending on match quality
                if presence >= IMAGE_MATCH_TOP or FORCE_CANDIDATE:
                    logging.info(
                        "File: " + filename + " - " + "{:.2f}".format(presence).rjust(6, " ") + " % - Candidate !"
                    )
                    target_path = os.path.join(FOLDER_IMAGE_MATCHED_TOP, os.path.basename(filepath))
                    utils.move_file(filepath, target_path)
                    images_top[target_path] = image

                elif presence >= IMAGE_MATCH_MID:
                    logging.info(
                        "File: " + filename + " - " + "{:.2f}".format(presence).rjust(6, " ") + " % - Not Candidate !"
                    )
                    target_path = os.path.join(FOLDER_IMAGE_MATCHED_MED, os.path.basename(filepath))
                    utils.move_file(filepath, target_path)
                    images_med[target_path] = image

                else:
                    logging.info(
                        "File: " + filename + " - " + "{:.2f}".format(presence).rjust(6, " ") + " % - Not Candidate !"
                    )
                    target_path = os.path.join(FOLDER_IMAGE_MATCHED_LOW, os.path.basename(filepath))
                    utils.move_file(filepath, target_path)
                    images_low[target_path] = image

    else:
        logging.debug("Skipped Image Processing !")

    if RUN_IMAGE_STORAGE:
        logging.info("=============== OUTLOOK ONEDRIVE ================")
        logging.info("Creating events in online storage")
        # get google calendar service helper
        session_creds = msgraph_services.authenticate(MS_CLIENT_ID, MS_SECRET_ID)
        calendar_service = msgraph_services.get_storage_service(session_creds)
        calendar_manager = MicrosoftStorageManager(calendar_service)

        logging.info('Uploading low-match files')
        calendar_manager.upload_files(list(images_low.keys()), MS_STORAGE_FOLDER_LOW)
        logging.info('Uploading medium-match files')
        calendar_manager.upload_files(list(images_med.keys()), MS_STORAGE_FOLDER_MED)
        logging.info('Uploading top-match files')
        calendar_manager.upload_files(list(images_top.keys()), MS_STORAGE_FOLDER_TOP)                

    if RUN_IMAGE_PARSING:
        logging.info("=============== IMAGE PARSER ===================")
        logging.info("OCR image and extract data as events")
        for path, image in images_top.items():
            parser = DancePlanningParser(path_to_tesseract)
            logging.info('Parsing: ' + path)
            parser.process(image=image, path=os.path.join(FOLDER_OUTPUT, "export.csv"))

    if RUN_DATA_STORAGE:
        logging.info("=============== DATA INTEGRATION ===============")
        logging.info("Connecting to database")
        mongo_client = MongoDB_Python(
            hostname=MONGODB_HOSTNAME,
            port=MONGODB_PORT,
            database=MONGODB_DATABASE,
            username=MONGODB_USERNAME,
            password=MONGODB_PASSWORD,
            collection="event",
        )
        if mongo_client:
            logging.info("Connected ! ")

        # insert events into database
        logging.info("Inserting events")
        try:
            for event in parser.planning.events:
                dict_event = event.to_json_storage()  # dict(event)
                if not mongo_client.exists(dict_event):
                    logging.info("Inserting: " + event.short_infos())
                    mongo_client.create(dict_event)
                else:
                    logging.info("Skipping: " + event.short_infos())
        except AttributeError as e:
            logging.info("No data to integrate !")
        except Exception as e:
            raise e

    if RUN_ONLINE_CALENDAR_GOOGLE:
        logging.info("=============== GOOGLE CALENDAR ================")
        # get google calendar service helper
        session_creds = google_services.authenticate()
        calendar_service = google_services.get_calendar_service(session_creds)
        calendar_manager = GoogleCalendarManager(calendar_service)
        logging.info('Connected to calendar !')
        try:
            for event in parser.planning.events:
                logging.info("Adding: " + event.short_infos())
                calendar_handler = calendar_manager.create_event(calendar_service, event)
        except AttributeError as e:
            logging.info("No data to integrate !")
        except Exception as e:
            raise e

    if RUN_ONLINE_CALENDAR_MS:
        logging.info("=============== OUTLOOK CALENDAR ===============")
        # get google calendar service helper
        session_creds = msgraph_services.authenticate(MS_CLIENT_ID, MS_SECRET_ID)
        calendar_service = msgraph_services.get_calendar_service(session_creds)
        calendar_manager = MicrosoftCalendarManager(calendar_service)
        logging.info('Connected to calendar !')
        try:
            for event in parser.planning.events:
                logging.info("Adding: " + event.short_infos())
                calendar_handler = calendar_manager.create_event(event, calendar_name="RockDancePlanning")
        except AttributeError as e:
            logging.info("No data to integrate !")
        except Exception as e:
            raise e

    if RUN_WHATSAPP_NOTIFIER:
        bot = WhatsappBot(config=whatsapp_services_config)
        bot.login()
        bot.send_message("TestWhatsApp", "Hello !")
        bot.send_message("TestWhatsApp", "It !")
        bot.send_message("TestWhatsApp", "Is !")
        bot.send_message("TestWhatsApp", "Me !")
        bot.close_and_quit()


if __name__ == "__main__":
    main()
