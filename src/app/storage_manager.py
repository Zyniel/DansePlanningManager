from distutils.command.install_egg_info import to_filename
import logging
import google_services
import msgraph_services
from O365.drive import Drive
from abc import ABC, abstractmethod
import os


class StorageManager(ABC):
    @abstractmethod
    def __init__(self, service):
        pass

    @abstractmethod
    def upload_files(self, local_file_paths, remote_folder_path):
        pass

    @abstractmethod
    def download_files(self, remote_file_paths, local_folder_path):
        pass

    @abstractmethod
    def delete_files(self, paths):
        pass

    @abstractmethod
    def create_folder(self, path):
        pass

    @abstractmethod
    def delete_folder(self, path):
        pass


class GoogleStorageManager(StorageManager):
    service = None

    def __init__(self, service):
        super().__init__(service)
        self.service = service

    def upload_files(self, local_file_paths, remote_folder_path):
        if type(local_file_paths) is not list:
            raise TypeError("TypeError: files is not a list")

    def download_files(self, remote_file_paths, local_folder_path):
        if type(remote_file_paths) is not list:
            raise TypeError("TypeError: files is not a list")

    def delete_files(self, paths):
        if type(paths) is not list:
            raise TypeError("TypeError: files is not a list")

    def create_folder(self, path):
        pass

    @abstractmethod
    def delete_folder(self, path):
        raise NotImplementedError

    def get_service():
        return google_services.get_storage_service()


class MicrosoftStorageManager(StorageManager):
    service: Drive = None

    def __init__(self, service):
        super().__init__(service)
        self.service = service  

    def upload_files(self, local_file_paths, remote_folder_path):
        if type(local_file_paths) is not list:
            raise TypeError("TypeError: files is not a list")

        folder_item = None
        # get the folder DriveItem
        if remote_folder_path == '/':
            folder_item = self.service.get_root_folder()
        else:
            folder_item = self.service.get_item_by_path(remote_folder_path)

        # found folder proceed to mass upload
        uploaded_items = []
        if folder_item:
            for local_path in local_file_paths:
                logging.info('Uploading: ' + local_path)
                item = folder_item.upload_file(item=local_path)
                uploaded_items.append(item)
        else:
            raise RuntimeError("RuntimeError: could not locate folder on OneDrive")

        return uploaded_items

    def download_files(self, remote_file_paths, local_folder_path):
        if type(remote_file_paths) is not list:
            raise TypeError("TypeError: files is not a list")

        if not os.path.exists(local_folder_path):
            os.makedirs(local_folder_path)

        downloaded_items = []
        # download each file to the local folder, retaining its original name
        if remote_file_paths:
            for remote_path in remote_file_paths:
                file_item = self.service.get_item_by_path(remote_path)
                operation = file_item.download(to_path=local_folder_path, to_filename=file_item.name)
                for status, progress in operation.check_status():
                    print("{} - {}".format(status, progress))

                downloaded_item = os.path.join(local_folder_path, file_item.name)
                downloaded_items.append(downloaded_item)

        return downloaded_items

    def delete_files(self, paths):
        if type(paths) is not list:
            raise TypeError("TypeError: files is not a list")

        # uploaded_file = folder.upload_file(item="path_to_my_local_file")

    def create_folder(self, path):
        pass

    def delete_folder(self, path):
        raise NotImplementedError

    def get_service(client_id, secret_id):
        return msgraph_services.get_calendar_service(client_id, secret_id)
