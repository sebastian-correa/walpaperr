import csv
from pathlib import Path
from shutil import copyfile

from . import WebSite


class CfgParser(object):
    def __init__(self, main_folder_name='walpaperr'):
        self.valid_sites = {test_class.__name__.lower() : test_class for test_class in WebSite.__subclasses__()}  # I call __name__ directly cause test_class is already a class "handle".
        
        self.path_obj = Path.home() / "Pictures" / main_folder_name / 'download_sites.cfg'
        if not self.path_obj.is_file():
            # Copy default .cfg file.
            copyfile(Path.cwd() / 'download_sites.cfg', self.path_obj)


    def get_all_valid_sites_from_cfg_file(self):
        valid_sites_from_cfg = []
        with open(self.path_obj, newline='') as cfg_file:
            cfg_file_reader = csv.reader(cfg_file)
            for row in cfg_file_reader:
                class_type, sub_site = row
                class_type = class_type.strip().lower()
                sub_site = sub_site.strip().lower()

                if class_type in self.valid_sites.keys():
                    instance = self.valid_sites[class_type](sub_site)
                    valid_sites_from_cfg.append(instance)
                    
        return valid_sites_from_cfg
