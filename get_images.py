"""
python3 get_images.py IMAGE_LINKS_FILENAME.txt ERROR_FILENAME.txt OUT_DIR_NAME
"""
import io
import logging
import os
import sys
import time

import requests
from PIL import Image

def get_image_name(image_link):
    """
    given link to jp2 image (e.g. 'https://chroniclingamerica.loc.gov/lccn/sn83045298/1963-12-20/ed-1/seq-1.jp2'),
    returns name of image by joining all parts of the url following and including the lccn value (e.g. sn83045298) with underscores
    """
    return ('_'.join(image_link.split('/')[4:])).strip()


def write_jp2_images(links_filename, out_dir):
    """
    writes all .jp2 images with links in links_filename as into out_dir
    """
    print("write_jp2_images")
    logging.info("Writing .jp2 images from " + links_filename + " into " + out_dir)
    start_time = time.time()
    count_successful = 0

    with open(links_filename, 'r') as links:
        for image_link in links:
            try:
                image_name = get_image_name(image_link)
                if not os.path.isfile(out_dir + '/' + image_name):
                    # pulls image
                    r = requests.get(image_link, stream=True)
                    # makes sure the request passed:
                    if r.status_code == 200:
                        with open(out_dir + '/' + image_name, 'wb') as f:
                            f.write(r.content)
                        count_successful += 1
                    else:
                        logging.warning("Request for image " + image_link + " failed with error code " + str(r.status_code))
            except:
                e = sys.exc_info()
                logging.error("Could not get image " + image_link + "; failed with error " + str(e))

    logging.info("Wrote " + str(count_successful) + " .jp2 images in " + str(time.time() - start_time) + " seconds")


def jp2s_to_jpgs(jp2s_dir):
    """
    converts jp2 files in jp2s_dir to jpgs
    """
    print("jp2s_to_jpgs")
    logging.info("Converting jp2s in " + jp2s_dir + " to jpgs")
    start_time = time.time()

    files = os.listdir(jp2s_dir)
    count = 0
    count_unsuccessful = 0
    for filename in os.listdir(jp2s_dir):
        count += 1
        try:
            convert_command = "gm convert " + jp2s_dir + "/" + filename + " " + jp2s_dir + "/" + filename.replace(".jp2", ".jpg")
            # convert_command = "mogrify -resize 100x100% -quality 100 -format jpg " + jp2s_dir + "/" + filename
            os.system(convert_command)
        except:
            logging.error(filename + "could not be converted to .jpg")
            count_unsuccessful += 1

        delete_command = "rm " + jp2s_dir + "/" + filename
        os.system(delete_command)
        logging.info("processed image " + str(count) + " of " + str(len(files)))
    # logging.info(".jp2 --> .jpg conversion done; deleting all .jp2 files")
    # delete_command = "rm " + jp2s_dir + "/*.jp2"
    # os.system(delete_command)

    logging.info("processed " + str(count) + " images total; " + str(count - count_unsuccessful) + " successful")
    logging.info(".jp2 --> .jpg conversion took " + str(time.time() - start_time) + " seconds")


def crop_resize_convert(dir, dim=1024):
    """
    crops all jpg images in `dir` to square dimensions (dim, dim) and saves
    """
    print("crop_resize_convert")
    logging.info("Running crop_resize_convert on " + dir + " to yield square images of dimension " + str(dim))
    start_time = time.time()
    Image.MAX_IMAGE_PIXELS = None # prevents large files from erroring because of DecompressionBombError

    for filename in os.listdir(dir):
        try:
            # resize to maintain aspect ratio
            img = Image.open(dir + "/" + filename)
            wpercent = (dim / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((dim, hsize), Image.ANTIALIAS)

            # crop image
            (left, upper, right, lower) = (0, 0, dim, dim)
            img = img.crop((left, upper, right, lower))

            img.save(dir + "/" + filename)
        except:
            logging.error("Something went wrong while resizing and converting " + filename)
    # logging.info("Crop/resize/.jpg conversion done; removing all .pngs")
    # delete_command = "rm " + dir + "/*.png"
    # os.system(delete_command)

    logging.info("crop_resize_convert took " + str(time.time() - start_time) + " seconds")


def main():
    args = sys.argv[1:]
    if len(args) != 3:
        print('Please specify filename of list of image links, filename for logging and out directory on command line')
        print('e.g.: python3 get_images.py IMAGE_LINKS_FILENAME.txt LOG_FILENAME.log OUT_DIR_NAME')
        return

    links_filename = args[0]
    log_filename = args[1]
    out_dir = args[2]
    logging.basicConfig(filename=log_filename, level=logging.INFO)

    start_time = time.time()

    write_jp2_images(links_filename, out_dir)
    jp2s_to_jpgs(out_dir)
    crop_resize_convert(out_dir)

    logging.info("The whole thing took " + str(time.time() - start_time) + " seconds")


if __name__ == '__main__':
    main()
