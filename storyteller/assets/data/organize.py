import sys
import json
import shutil
import random
import argparse
from pathlib import Path


def split_data(folder, train_size):
    """Splits data into train and validation sets.

    Arguments:
    ----------
        folder (pathlib.Path):
            Path to images folder.
        train_size (float):
            Percentage of files in train set.

    Returns:
    --------
        train_images, val_images (tuple):
            List of images belonging to train and validation sets
            respectively.
    """
    images = list(folder.iterdir())
    n_train = int(train_size * len(images))

    train_images = random.sample(images, n_train)
    val_images = [img for img in images if img not in train_images]

    return train_images, val_images


def move_images(folder, train_images, val_images):
    """Copy images in `folder` into train and validation folders.
    Original folder is deleted.

    Arguments:
    ----------
        folder (pathlib.Path):
            Path to images folder.
        train_images (list):
            List of image file names in trianing set.
        val_images (list):
            List of image file names in validation set.
    """
    train_folder, val_folder = Path('images/train'), Path('images/val')

    train_folder.mkdir(exist_ok=True)
    val_folder.mkdir(exist_ok=True)

    for img in train_images:
        shutil.copy(img, train_folder / img.name)

    for img in val_images:
        shutil.copy(img, val_folder / img.name)


def txt_to_json(file, val_images):
    """Create JSON files for captions in train and validation sets.

    Arguments:
    ----------
        file (pathlib.Path):
            Path to file containing captions.
        val_images (list):
            List of image file names in validation set.
    """
    file = Path(file)
    val_images = set(val_images)
    train_captions, val_captions = [], []

    with open(file, 'r') as fileobj:
        lines = fileobj.readlines()

    for line in lines[1:]:
        items = line.split(',')
        filename, caption = items[0], ','.join(items[1:])

        # Considering valiation set is much smaller than the train-set,
        # it is optimal to check membership with this.
        _item = {
        	"image_id": items[0],
        	"caption": caption
        }
        if filename in val_images:
            val_captions.append(_item)
        else:
            train_captions.append(_item)

    with open('images/train_captions.json', 'w') as fileobj:
        json_contents = {
            'dataset': 'flickr8k',
            'contents': train_captions
        }
        json.dump(json_contents, fileobj, indent=4)

    with open('images/val_captions.json', 'w') as fileobj:
        json_contents = {
            'dataset': 'flickr8k',
            'contents': val_captions
        }
        json.dump(json_contents, fileobj, indent=4)


def remove(folder, file):
    """Remove redundant files/folders upon successful completion of
    data organization.

    Arguments:
    ----------
        folder (pathlib.Path):
            Path to images folder.
        file (pathlib.Path):
            Path to file containing captions.   
    """
    shutil.rmtree(folder)
    file.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Organize data for show-and-tell.')
    parser.add_argument('--images', dest='images_folder', type=str,
                        default='images/flickr8k', help='Image directory name.')
    parser.add_argument('--captions', dest='captions', type=str,
                        default='images/captions.txt', help='File containing captions.')
    parser.add_argument('--train_size', dest='train_size', type=float,
                        default=0.8, help='\% of files in train-set')

    args = parser.parse_args()

    images_path = Path(args.images_folder)
    captions_file = Path(args.captions)

    if images_path.exists() and captions_file.exists():
        train_imgs, val_imgs = split_data(images_path, args.train_size)
        move_images(images_path, train_imgs, val_imgs)
        txt_to_json(captions_file, val_imgs)
        remove(images_path, captions_file)
    else:
        msg = ("Download flickr64 dataset from the following link: "
               "https://www.kaggle.com/adityajn105/flickr8k?select=captions.txt")
        sys.exit(msg)
