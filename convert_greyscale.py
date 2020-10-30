import os
from PIL import Image

IMAGES_DIR = '1900_unique_1123'
# IMAGES_DIR = '1959_1003'

OUT_DIR = '1900_unique_1123_greyscale'

def main():
    for filename in os.listdir(IMAGES_DIR):
        Image.open(IMAGES_DIR + '/' + filename).convert('L').save(OUT_DIR + '/' + filename)


if __name__ == "__main__":
    main()
