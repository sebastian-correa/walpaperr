import requests
from .image import Image

from datetime import datetime
import csv
import time
from pathlib import Path


class Reddit(object):
    mainUrl = 'https://www.reddit.com'

    def __init__(self, subreddit='wallpaper', lastRequestURL='', image=''):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                                      'like Gecko) Chrome/60.0.3112.113 Safari/537.36'}

        self.subreddit = subreddit  # TODO: Change to site.
        self.lastRequestURL = lastRequestURL

        self.last_request_json = {}
        self.image_dict = {}
        self.image = image

        self.date_format = '%d/%b/%Y'

    # Setters
    def set_json(self, sort='hour', limit=25):
        requestUrl: str = Reddit.mainUrl + "/r/" + self.subreddit + '/top/.json?sort=' + sort + '?limit=' + str(limit)
        self.lastRequestURL = requestUrl

        success = False
        limit = 5
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

    def set_image_obj_from_last_json(self, valid_index=0):
        # valid_index: from where to start the search for a valid image.
        valid_index = self.get_valid_index_for_photo(index=valid_index)

        self.image_dict = self.last_request_json['data']['children'][valid_index]

        url = self.image_dict['data']['url']
        site = self.subreddit
        image_name = url.split('/')[-1]  # Last item of the array splitted by '/'
        vRes, hRes = self.get_best_resolution()

        self.image = Image(url=url, site=site, image_name=image_name, vRes=vRes, hRes=hRes, index_in_dict=valid_index)


    # Getters
    def get_best_resolution(self):
        return self.image_dict['data']['preview']['images'][0]['source']['height'], \
               self.image_dict['data']['preview']['images'][0]['source']['width']

    def get_valid_index_for_photo(self, index=0):
        # Some posts won't contain an image. I use reddit's "post_hint" field to find an image.
        # This might not work, but I haven't found a use-case where it breaks.
        # By default attempts with the first item in list.
        amount_of_entries = self.last_request_json['data']['dist']
        while self.last_request_json['data']['children'][index]['data']['post_hint'] != 'image':
            index += 1
            if index >= amount_of_entries:
                return False  # index went out of bounds and din't find any image.
        return index

    def get_image_obj_from_last_json(self, valid_index=0):
        self.set_image_obj_from_last_json(valid_index)
        return self.image

    # Others
    def delete_images_older_than_days(self, older_than=5, folder_name='walpaperr'):
        filename = self.subreddit + ".csv"
        csv_path = Path.home() / "Pictures" / folder_name / self.subreddit / filename
        if csv_path.is_file(): # Only read it if it exists.
            with open(csv_path, 'r') as f:
                reader = csv.reader(f)
                today_date = datetime.today()

                for row in reader:
                    download_date = datetime.strptime(row[-1], self.date_format)
                    delta = today_date - download_date

                    if delta.days > older_than:
                        image_name = row[2]
                        i = Image(site=self.subreddit, image_name=image_name, folder_name=folder_name)
                        i.delete()

print("Reddit loaded.")
