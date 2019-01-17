import time
import requests
import classes as c


# TODO: Refactor this to handle_reddit()
def main(site_array, time_between_changes=0 * 3600 + 0 * 60 + 30):
    site_index = 0
    max_number_of_retries = 5

    while True:
        # Current wallpaper should be from site that has index = index - 1:
        current_wallpaper = site_array[(site_index - 1) % len(site_array)].image

        s = site_array[site_index % len(site_array)]  # Select NEW site to download from.
        s.delete_images_older_than_days()

        if s.set_json():  # Get dict from top posts successfully.
            new_image_downloaded = False
            index = 0  # Where to start looking for a valid image.
            retries = 0

            while not new_image_downloaded and retries <= max_number_of_retries:  # While no new image is accepted...
                # Assign site's new image to the one at INDEX to attempt to download.
                new_image = s.get_image_obj_from_last_json(index)

                try:
                    new_image.download()
                    # download() raises exceptions for a file that exists and for a download error.
                    # If download() runs correctly, I check with SSIM just in case of a repost.

                    if new_image.compare_to_image(current_wallpaper):
                        # If downloaded image is the same as my current wallpaper, I discard it.
                        # Inside a site's folder, names should be unique, so repeats shouldn't happen.
                        new_image.delete()
                        index += 1
                        retries += 1
                    else:
                        # Images are different.
                        new_image.save_image_data_to_file()
                        new_image.set_desktop_background()
                        new_image_downloaded = True
                except FileExistsError:
                    # An image with the same name already exists.
                    index += 1
                    retries += 1
                except requests.exceptions.RequestException as e:
                    # An error occurred while downloading.
                    # I'll attempt another one (after 1 minute) so I don't have to fix it.
                    index += 1
                    retries += 1
                    time.sleep(60)
        else:
            pass

        site_index += 1
        time.sleep(time_between_changes)


if __name__ == '__main__':
    # s_array = [c.Desktoprr(site='desktoprr'), c.Reddit(subreddit='wallpaper'), c.Reddit(subreddit='wallpapers'), c.Reddit(subreddit='earthporn'),c.Reddit(subreddit='cityporn'), c.Reddit(subreddit='skyporn'), c.Reddit(subreddit='weatherporn'), c.Reddit(subreddit='villageporn'), c.Reddit(subreddit='spaceporn')]
    s_array = [c.Desktoprr(site='desktoprr')]

    # TODO: For now, only pulls from Reddit. Refactor desktoprr to have same names as reddit. Or get class and act upon
    main(site_array=s_array)