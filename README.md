# cs230_nonsense_newspapers
This repo contains code I wrote for my CS230 final project. I also wrote a website from scratch to present the final outputs; that repo can be found [here](https://github.com/mirandali707/nonsense_newspapers).

## Files
* `convert_greyscale.py`: converts all images in directory to 1-channel greyscale
* `get_front_pages.ipynb`: writes manifest files from which images are downloaded, uses Library of Congress Newspaper Navigator API structure
* `get_images.py`: downloads images from links in text files created by `get_front_pages.ipynb` into specified directory
* `is this loss.ipynb`: notebook for visualizing G/D loss during training
* `outputs`: directory containing 20 generated outputs at each scale
