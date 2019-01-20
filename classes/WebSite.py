import csv
import time
from abc import ABCMeta, abstractmethod
from datetime import datetime
from pathlib import Path

import requests

from .image import Image


class WebSite(object, metaclass=ABCMeta):
    """
    Main Website class. Holds common attributes and methods.
    """

    def __init__(self, main_url, sub_site, main_folder_name='walpaperr', lastRequestURL='', image=''):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                                'like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
        self.main_url = main_url
        self.sub_site = sub_site
        self.date_format = '%d/%b/%Y'

        self.lastRequestURL = lastRequestURL
        self.last_request_json = {}
        self.image_dict = {}
        self.image = image

        self.request_retry_max_attempts = 5

        self.main_folder_name = main_folder_name
        self.path_obj = Path.home() / "Pictures" / main_folder_name / type(self).__name__ / self.sub_site  # type(self).__name__ -> Gets instance's class and then grabs name (gets self's class and then name)

    def __str__(self):
        return self.main_url + "/" + self.sub_site

    def request_url_with_retry(self, request_url, max_retry_attempts=None):
        max_retry_attempts = max_retry_attempts if max_retry_attempts is not None else self.request_retry_max_attempts  #Cannot pass self.XXX as default argument.
        self.last_request_url = request_url

        success = False
        attempts = 0

        while not success and attempts <= max_retry_attempts:
            try:
                r = requests.get(request_url, headers=self.headers)
                success = True
            except requests.exceptions.RequestException:
                attempts += 1
                time.sleep(15)

        if r.status_code == 200:
            self.last_request_json = r.json()
            return True
        else:
            return False

    def delete_images_older_than_days(self, older_than=5):
        csv_filename = self.sub_site + ".csv"
        csv_path =  self.path_obj / csv_filename
        if csv_path.is_file(): # Only read it if it exists.
            with open(csv_path, 'r') as f:
                reader = csv.reader(f)
                today_date = datetime.today()

                for row in reader:
                    try:
                        download_date = datetime.strptime(row[-1], self.date_format)
                        delta = today_date - download_date

                        if delta.days > older_than:
                            image_name = row[2]
                            i = Image(web_site=type(self).__name__, sub_site=self.sub_site, image_name=image_name, main_folder_name=self.main_folder_name)
                            i.delete()
                    except ValueError:
                        # Dateformat is wrong. Do not delete the photo but tell the user.
                        print('Image @ ' + self.sub_site + " " + row[2] + ' requires action. Wrong date format.')

    @abstractmethod
    def set_json(self):
        pass

    @abstractmethod
    def get_image_obj(self, image_number=0):
        pass        

#TODO: Don't delete after time button.
#TODO: Download from all sites in download_sites.cfg
