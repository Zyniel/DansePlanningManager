import logging
import google_services
import msgraph_services
from O365.calendar import Schedule
from abc import ABC, abstractmethod
from image_parser import Event


class CalendarManager(ABC):

    @abstractmethod
    def __init__(self, service):
        pass

    @abstractmethod
    def create_event(self, event: Event, calendar : str):
        pass

    @abstractmethod
    def delete_event(self, event: Event, calendar : str):
        pass

    @abstractmethod
    def search_event(self, event: Event, calendar : str):
        pass

    @abstractmethod
    def get_calendars(self, calendar : str):
        pass

    @abstractmethod
    def delete_calendar(self, calendar : str):
        pass

    @abstractmethod
    def create_calendar(self, calendar : str):
        pass

    @staticmethod
    @abstractmethod
    def get_service():
        pass


class GoogleCalendarManager(CalendarManager):
    service = None

    def __init__(self, service):
        super().__init__(service)
        self.service = service

    def create_event(self, event: Event, calendar_name : str, color):
        event_result = self.service.events().insert(calendarId='primary',
            body={
                "summary": event.description,
                "description": event.description,
                "start": {"dateTime": event.start_date.isoformat(), "timeZone": 'Europe/Paris'},
                "end": {"dateTime": event.end_date.isoformat(), "timeZone": 'Europe/Paris'},
            }
        ).execute()
        logging.debug(event_result)

        return event_result     


    def delete_event(self, event: Event, calendar : str):
        pass

    def search_event(self, event: Event, calendar : str):
        pass

    def get_calendars(self, calendar : str):
        pass

    def delete_calendar(self, calendar : str):
        pass

    def create_calendar(self, calendar : str):
        pass

    def get_service():
        return google_services.get_calendar_service()


class MicrosoftCalendarManager(CalendarManager):
    service : Schedule = None

    def __init__(self, service):
        super().__init__(service)
        self.service = service

    def create_event(self, event: Event, calendar_name : str, color = None):
        event_result = None

        if event: 
            calendar = self.service.get_calendar(calendar_name=calendar_name)

            new_event = calendar.new_event()
            new_event.subject = event.description
            
            if event.location and event.location != "":
                new_event.location = event.location
            
            new_event.start = event.start_date

            if event.end_date:
                new_event.end = event.end_date

            event_result = new_event.save()
        else:
            raise RuntimeError('Event does not exist !')

        return event_result     


    def delete_event(self, event: Event, calendar : str):
        pass

    def search_event(self, event: Event, calendar : str):
        pass

    def get_calendars(self, calendar_name : str = None):
        calendar = []

        if not calendar_name is None:
            calendar = [ self.service.get_calendar(calendar_name=calendar_name) ]
        else:
            calendar = self.service.list_calendars()
        
        return calendar

    def delete_calendar(self, calendar : str):
        pass

    def create_calendar(self, calendar : str):
        pass

    def get_service(client_id, secret_id):
        return msgraph_services.get_calendar_service(client_id, secret_id)