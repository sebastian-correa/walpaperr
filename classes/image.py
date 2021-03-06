import csv
import ctypes
import os
import shutil
from datetime import datetime
from pathlib import Path

import requests
from skimage.measure import compare_ssim as ssim

import cv2


class Image(object):
    """
    The Image class implements some methods to handle images.

    It creates a folder in the user's Pictures folder and places downloaded images in a subfolder named "site".
    It can download images, set them as backgrounds and check their resolution.
    """

    def __init__(self, url='', web_site='', sub_site='', image_name='', vRes='', hRes='', main_folder_name='walpaperr'):
        self.main_folder_name = main_folder_name
        self.date_format = '%d/%b/%Y'
        # name = whatever_the_file_is_named_on_the_server.extension (this way, it is unique).
        self.url: str = url  # Direct URL to image.

        self.web_site: str = web_site  # main site: i.e reddit, desktoprr
        self.sub_site: str = sub_site  # sub_site: i.e subreddit, desktoprr
        self.vRes: str = vRes  # vertical resolution
        self.hRes: str = hRes  # horizontal resolution
        self.image_name: str = image_name

        self.path_obj = Path.home() / "Pictures" / main_folder_name / web_site / sub_site / image_name
        self.create_folder()

    def create_folder(self):
        try:
            os.makedirs(self.path_obj.parent)
        except FileExistsError:  # If it already exists, pass.
            pass
        return True

    def download(self):
        # Images are to be saved in absolute_path/site_name/image_name.extension (path created on __init__).
        result = False
        if not os.path.isfile(self.path_obj):  # File doesn't exist:
            r = requests.get(self.url, stream=True)
            if r.status_code == 200:  # Request returns correctly.
                with open(self.path_obj, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
                del r
                result = True
            else:
                print("Error " + r.status_code + " when requesting " + self.url)
        else:
            print("The file @ " + str(self.path_obj) + " already exists.")
            raise FileExistsError
        return result

    def delete(self):
        try:
            Path.unlink(self.path_obj)
        except FileNotFoundError:
            #File doesn't exist. I don't need to delete it.
            pass
        return True

    def save_image_data_to_file(self):
        row = [self.url, self.sub_site, self.image_name, self.vRes, self.hRes, datetime.today().strftime(self.date_format)]
        filename = self.sub_site + ".csv"
        csv_path = self.path_obj.parent / filename
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)

    @staticmethod
    def acceptable_resolution(hRes, vRes):
        # Resolution is acceptable if some dimension is > 720p.
        # TODO: Finish this method.
        # In list of as[ect ratios.
        # Greater than 1366 x 768
        pass

    def resolutions_match(self, compareToThisImage):
        if self.hRes == compareToThisImage.hRes and self.vRes == compareToThisImage.vRes:
            return True
        else:
            return False

    def set_desktop_background(self):
        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, str(self.path_obj), 0)

    def compare_to_image(self, compareToThisImage, tolerance: float =.95) -> bool:
        # I contemplate the case where the site has never been run by checking compareToThisImage == ''.
        # True means they are the same.

        if compareToThisImage == '':
            return False
        else:
            if self.resolutions_match(compareToThisImage):
                # Load the images
                instanceImage = cv2.imread(self.path_obj.absolute().as_posix())
                compareToThisImage = cv2.imread(compareToThisImage.path_obj.absolute().as_posix())

                # convert the images to grayscale
                instanceImage = cv2.cvtColor(instanceImage, cv2.COLOR_BGR2GRAY)
                compareToThisImage = cv2.cvtColor(compareToThisImage, cv2.COLOR_BGR2GRAY)

                s = ssim(instanceImage, compareToThisImage)
                if s >= tolerance:
                    return True
                else:
                    return False
            else:
                return False
