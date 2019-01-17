import requests
from .image import Image

from datetime import datetime
import csv
import time
from pathlib import Path


class Desktoprr(object):
    mainUrl = 'https://api.desktoppr.co'

    def __init__(self, site='desktoprr', lastRequestURL='', image=''):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                                      'like Gecko) Chrome/60.0.3112.113 Safari/537.36'}

        self.last_request_url = lastRequestURL
        self.image = image
        self.site = site

        self.last_request_json = {}
        self.image_dict = {}
        self.date_format = '%d/%b/%Y'

    # Getters
    def get_best_resolution(self):
        return self.image_dict['height'], self.image_dict['width']

    def get_image_obj_from_last_json(self, index=0):
        self.set_image_obj_from_last_json(index=index)
        return self.image

    # Setters
    def request_url_with_retry(self, requestUrl, limit=5):
        self.last_request_url = requestUrl

        success = False
        attempts = 0

        while not success and attempts <= limit:
            try:
                r = requests.get(requestUrl, headers=self.headers)
                success = True
            except requests.exceptions.RequestException as e:
                attempts += 1
                time.sleep(15)

        if r.status_code == 200:
            self.last_request_json = r.json()
            return True
        else:
            return False

    def set_json_sfw_wallpaper_page(self, page=1):
        requestUrl: str = Desktoprr.mainUrl + '/1/wallpapers?page=' + str(page)
        return self.request_url_with_retry(requestUrl=requestUrl) #True or False depending on request.

    def set_json_random_sfw_image(self):
        requestUrl: str = Desktoprr.mainUrl + '/1/wallpapers/random'
        return self.request_url_with_retry(requestUrl=requestUrl) #True or False depending on request.

    def set_json(self, where='page'):
        # Basically a wrapper for where to set the json from.
        if where == 'page':
            self.set_json_sfw_wallpaper_page()
        elif where == 'random':
            self.set_json_random_sfw_image()
        return True

    def set_image_dict_from_last_json(self, index=0):
        try:
            # Case: I get list of images.
            self.image_dict = self.last_request_json['response'][index]
        except KeyError:
            # Case: I get the image directly.
            self.image_dict = self.last_request_json['response']

    def set_image_obj_from_last_json(self, index=0):
        self.set_image_dict_from_last_json(index=index)

        url = self.image_dict['image']['url']
        image_name = url.split('/')[-1]  # Last item of the array split by '/'
        vRes, hRes = self.get_best_resolution()

        self.image = Image(url=url, site='desktoprr', image_name=image_name, vRes=vRes, hRes=hRes, index_in_dict=index)

    # Others
    def delete_images_older_than_days(self, older_than=5, folder_name='walpaperr'):
        filename = self.site + ".csv"
        csv_path = Path.home() / "Pictures" / folder_name / self.site / filename

        if csv_path.is_file(): # Only read it if it exists.
            with open(csv_path, 'r') as f:
                reader = csv.reader(f)
                today_date = datetime.today()

                for row in reader:
                    # TODO: Don't compute delta for every row. Add a character to indicate from where to check delta. To help speed.
                    download_date = datetime.strptime(row[-1], self.date_format)
                    delta = today_date - download_date

                    if delta.days > older_than:
                        image_name = row[2]
                        i = Image(site=self.site, image_name=image_name, folder_name=folder_name)
                        i.delete()
