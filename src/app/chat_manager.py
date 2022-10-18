import logging
from abc import ABC, abstractmethod

class ChatManager(ABC):

    @abstractmethod
    def message_contact(self, contact_id, message):
        pass

    @abstractmethod
    def message_group(self, contact_id, message):
        pass    

    @staticmethod
    @abstractmethod
    def get_service():
        pass


class WhatsappChatManager(ABC):

    @abstractmethod
    def message_contact(self):
        pass

    @staticmethod
    @abstractmethod
    def get_service():
        pass    