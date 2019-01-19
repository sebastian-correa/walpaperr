import csv
import time
from datetime import datetime
from pathlib import Path

import requests

from .image import Image
from .WebSite import WebSite


class Desktoprr(WebSite):

    def __init__(self, sub_site='desktoprr', lastRequestURL='', image=''):
        super().__init__(main_url='https://api.desktoppr.co', sub_site=sub_site, lastRequestURL=lastRequestURL, image=image)

    # Setters
    def set_json(self, where='page'):
        """
        Saves the request json in the class' attribute (contains many pictures).
        """
        # Basically a wrapper for where to set the json from.
        if where == 'page':
            return self.set_json_sfw_wallpaper_page()
        elif where == 'random':
            return self.set_json_random_sfw_image()

    def set_json_sfw_wallpaper_page(self, page=1):
        request_url: str = self.main_url + '/1/wallpapers?page=' + str(page)
        return self.request_url_with_retry(request_url=request_url) #True or False depending on request.

    def set_json_random_sfw_image(self):
        request_url: str = self.main_url + '/1/wallpapers/random'
        return self.request_url_with_retry(request_url=request_url) #True or False depending on request.

    def set_image_dict_from_last_json(self, index=0):
        try:
            # Case: I get list of images.
            self.image_dict = self.last_request_json['response'][index]
        except KeyError:
            # Case: I get the image directly.
            self.image_dict = self.last_request_json['response']

    def set_image_obj_from_image_dict(self):
        url = self.image_dict['image']['url']
        sub_site = self.sub_site
        image_name = url.split('/')[-1]  # Last item of the array split by '/'
        vRes, hRes = self.get_best_resolution()

        self.image = Image(url=url, web_site=type(self).__name__, sub_site=sub_site, image_name=image_name, vRes=vRes, hRes=hRes)
  
    # Getters
    def get_best_resolution(self):
        return self.image_dict['height'], self.image_dict['width']

    def get_image_obj(self, image_number=0):
        self.set_image_dict_from_last_json(index=image_number)
        self.set_image_obj_from_image_dict()
        return self.image
    