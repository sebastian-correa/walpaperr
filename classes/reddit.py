import csv
import time
from datetime import datetime
from pathlib import Path

import requests

from .image import Image
from .WebSite import WebSite


class Reddit(WebSite):

    def __init__(self, subreddit='wallpaper', lastRequestURL='', image=''):
        super().__init__(main_url='https://www.reddit.com', sub_site=subreddit, lastRequestURL=lastRequestURL, image=image)

    def __str__(self):
        return self.main_url + "/r/" + self.sub_site

    # Setters
    def set_json(self, sort='hour', limit=25):
        """
        Saves the request json in the class' attribute (contains many pictures).
        """
        request_url: str = self.main_url + "/r/" + self.sub_site + '/top/.json?sort=' + sort + '?limit=' + str(limit)
        return self.request_url_with_retry(request_url=request_url) #True or False depending on request.

    def set_image_dict_from_last_json(self, search_start_index=0):
        valid_index = self.get_valid_index_for_photo(search_start_index=search_start_index)
        self.image_dict = self.last_request_json['data']['children'][valid_index]

    def set_image_obj_from_image_dict(self):
        # valid_index: from where to start the search for a valid image (see explanation in get_valid_index_for_photo)
        url = self.image_dict['data']['url']
        sub_site = self.sub_site
        image_name = url.split('/')[-1]  # Last item of the array splitted by '/'
        vRes, hRes = self.get_best_resolution()

        self.image = Image(url=url, web_site=type(self).__name__, sub_site=sub_site, image_name=image_name, vRes=vRes, hRes=hRes)

    # Getters
    def get_best_resolution(self):
        return self.image_dict['data']['preview']['images'][0]['source']['height'], \
               self.image_dict['data']['preview']['images'][0]['source']['width']

    def get_valid_index_for_photo(self, search_start_index=0):
        # Some posts won't contain an image. I use reddit's "post_hint" field to find an image.
        # This might not work, but I haven't found a use-case where it breaks.
        # By default attempts with the first item in list.
        index = search_start_index
        amount_of_entries = self.last_request_json['data']['dist']
        while self.last_request_json['data']['children'][index]['data']['post_hint'] != 'image':
            index += 1
            if index >= amount_of_entries:
                return False  # index went out of bounds and din't find any image.
        return index

    def get_image_obj(self, image_number=0):
        self.set_image_dict_from_last_json(search_start_index=image_number)
        self.set_image_obj_from_image_dict()
        return self.image
