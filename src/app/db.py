#!/usr/bin/python
# coding: utf-8

from pymongo import MongoClient
import logging
from abc import ABC, abstractmethod


class JSONStorage(ABC):
    """
    """
    @abstractmethod
    def create(self, query={}):
        pass

    @abstractmethod
    def read(self, query={}):
        pass

    @abstractmethod
    def update(self, query_1={}, query_2={}):
        pass

    @abstractmethod
    def delete(self):
        pass


class MongoDB_Python(JSONStorage):
    """
    """
    def __init__(self, hostname, port, database, username, password, collection):
        try:
            # Initialize the connection on the data base.
            self.conn = MongoClient(host=hostname, port=port, username=username, password=password)
            self.db = self.conn[database]
            self.cursor = self.db.get_collection(collection)
        except Exception as e:
            logging.error("Failed to connect to MongoDB !")
            raise e

    def create(self, query={}):
        # Insert a new register.
        id = self.cursor.insert_one(query)
        logging.debug('MongoDB: Inserted event: ' + str(id.inserted_id))

    def read(self, query={}):
        # Read all the register.
        for value in self.cursor.find(query):
            print(value)

    def exists(self, query={}):
        # Read all the register.
        id = self.cursor.find_one(query)
        return not id is None
            
    def update(self, query_1={}, query_2={}):
        # Change the first item on the list.
        id = self.cursor.update(query_1, query_2)
        logging.debug('MongoDB: Inserted event: ' + str(id.inserted_id))

    def delete(self):
        # Delete all the elements on the list.
        for i in self.cursor.find():
            id = self.cursor.remove(i)
            logging.debug('MongoDB: Deleted event: ' + str(id.inserted_id))

    def list_databases(self):
        # List all databases
        for db in self.conn.list_databases():
            print(db)
