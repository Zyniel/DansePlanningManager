#!/usr/bin/python
# coding: utf-8

import logging
import os
import ruamel.yaml as yaml


class Config(object):
    """ """

    def __init__(self, conf):
        self._config = conf  # set it to conf

    def get_property(self, property_name):
        try:
            parts = property_name.split(".")
            tempdict = self._config
            for count, part in enumerate(parts):
                tempdict = tempdict[part]

            return tempdict
        except Exception as e:
            return None

    @staticmethod
    def load(path):

        with open(path) as file:
            conf = yaml.safe_load(file)
        return conf


class AppGlobalConfig(Config):
    @property
    def environment(self):
        return self.get_property("app.environment")

    @property
    def debug(self):
        return self.get_property("app.debug")


class MongoConfig(Config):
    @property
    def host(self):
        return self.get_property("databases.mongodb.host")

    @property
    def port(self):
        return self.get_property("databases.mongodb.port")

    @property
    def db_name(self):
        return self.get_property("databases.mongodb.db")

    @property
    def username(self):
        return os.getenv("MONGODB_USERNAME")

    @property
    def password(self):
        return os.getenv("MONGODB_PASSWORD")


class AppScrapperConfig(Config):
    @property
    def pages(self):
        return self.get_property("app.scrapper.pages")

    @property
    def username(self):
        return os.getenv("FACEBOOK_USERNAME")

    @property
    def password(self):
        return os.getenv("FACEBOOK_PASSWORD")

    @property
    def search_depth(self):
        return self.get_property("app.scrapper.search-depth")

    @property
    def safety_delay(self):
        return self.get_property("app.scrapper.safety-delay")


class AppParserConfig(Config):

    @property
    def executable(self):
        return self.get_property("app.parser.tesseract-exe")
        
    @property
    def output_folder(self):
        return self.get_property("app.folders.output")

    @property
    def download_folder(self):
        return self.get_property("app.folders.images-downloaded")

    @property
    def low_match_folder(self):
        return self.get_property("app.folders.images-matched-low")

    @property
    def med_match_folder(self):
        return self.get_property("app.folders.images-matched-med")

    @property
    def top_match_folder(self):
        return self.get_property("app.folders.images-matched-top")

    @property
    def top_match(self):
        return self.get_property("app.parser.match-top-threshold")

    @property
    def med_match(self):
        return self.get_property("app.parser.match-med-threshold")

    @property
    def detection_lower_hsv(self):
        hsv = self.get_property("app.parser.detection-lower-color-hsv")
        return [hsv[0], hsv[1], hsv[2]]

    @property
    def detection_upper_hsv(self):
        hsv = self.get_property("app.parser.detection-upper-color-hsv")
        return [hsv[0], hsv[1], hsv[2]]


class MicrosoftServiceConfig(Config):
    
    @property
    def client_id(self):
        return os.getenv("MS_CLIENT_ID")        

    @property
    def secret_id(self):
        return os.getenv("MS_SECRET_ID")        

    @property
    def calendar_enabled(self):
        return bool(self.get_property("app.calendars.microsoft.enabled"))

    @property
    def storage_enabled(self):
        return bool(self.get_property("app.storage.microsoft.enabled"))        

    @property
    def storage_folder_low(self):
        return self.get_property("app.storage.microsoft.folder-matched-low")

    @property
    def storage_folder_med(self):
        return self.get_property("app.storage.microsoft.folder-matched-med")

    @property
    def storage_folder_top(self):
        return self.get_property("app.storage.microsoft.folder-matched-top")        


class GoogleServiceConfig(Config):
    @property
    def client_id(self):
        return os.getenv("GOOGLE_CLIENT_ID")       

    @property
    def secret_id(self):
        return os.getenv("GOOGLE_SECRET_ID")

    @property
    def calendar_enabled(self):
        return bool(self.get_property("app.services.google.enabled"))   

    @property
    def storage_enabled(self):
        return bool(self.get_property("app.storage.google.enabled")) 

    @property
    def storage_folder(self):
        return self.get_property("app.storage.google.folder")

    @property
    def storage_folder_low(self):
        return self.get_property("app.storage.google.folder-matched-low")

    @property
    def storage_folder_med(self):
        return self.get_property("app.storage.google.folder-matched-med")

    @property
    def storage_folder_top(self):
        return self.get_property("app.storage.google.folder-matched-top")  


class WhatsappServiceConfig(Config):
    @property
    def user_dir_folder(self):
        return self.get_property("app.notifiers.whatsapp.user-dir-folder")

    @property
    def enabled(self):
        return bool(self.get_property("app.notifiers.whatsapp.enabled"))        