"""
python3 get_images.py IMAGE_LINKS_FILENAME.txt ERROR_FILENAME.txt OUT_DIR_NAME
"""
# import PIL
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
    return ('_'.join(image_link.split('/')[4:])).strip()[:-1] + 'g'


def write_jp2_images(links_filename, out_dir):
    """
    writes all .jp2 images with links in links_filename as into out_dir
    """
    logging.info(f"Writing .jp2 images from {links_filename} into {out_dir}")
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
                        logging.warning(f"Request for image {image_link} failed with error code {r.status_code}")
            except:
                e = sys.exc_info()
                logging.error(f"Could not get image {image_link}; failed with error {str(e)}")

    logging.info(f"Wrote {count_successful} .jp2 images in {time.time() - start_time} seconds")


def jp2s_to_pngs(jp2s_dir):
    """
    replaces jp2s in `jp2s_dir` with pngs (converts to pngs and deletes all jp2s)
    """
    logging.info(f"Converting jp2s in {jp2s_dir} to pngs")
    start_time = time.time()

    convert_command = f"opj_decompress -ImgDir {jp2s_dir} -OutFor png"
    os.system(convert_command)

    logging.info(".jp2 --> .png conversion done; deleting all .jp2 files")
    delete_command = f"rm {jp2s_dir}/*.jp2"
    os.system(delete_command)

    logging.info(f".jp2 --> .png conversion took {time.time() - start_time} seconds")


def crop_resize_convert(pngs_dir, dim=1024):
    """
    crops all png images in `pngs_dir` to square dimensions (dim, dim), saves as jpg, and deletes all pngs
    """
    logging.info(f"Running crop_resize_convert on {pngs_dir} to yield square images of dimension {dim}")
    start_time = time.time()

    for filename in os.listdir(pngs_dir):
        try:
            # resize to maintain aspect ratio
            img = Image.open(f"{pngs_dir}/{filename}")
            wpercent = (dim / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((dim, hsize), Image.ANTIALIAS)

            # crop image
            (left, upper, right, lower) = (0, 0, dim, dim)
            img = img.crop((left, upper, right, lower))

            img.save(f"{pngs_dir}/{filename[:-4]}.jpg")
        except:
            logging.error(f"Something went wrong while resizing and converting {filename}")
    logging.info("Crop/resize/.jpg conversion done; removing all .pngs")
    delete_command = f"rm {pngs_dir}/*.png"
    os.system(delete_command)

    logging.info(f"crop_resize_convert took {time.time() - start_time} seconds")


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

    write_jp2_images(links_filename, out_dir)
    jp2s_to_pngs(out_dir)
    crop_resize_convert(out_dir)


if __name__ == '__main__':
    main()
