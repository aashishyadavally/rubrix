import sys
import json
import shutil
import argparse
import zipfile
import shutil
import subprocess
from pathlib import Path

from storyteller import pathfinder


DATASET_ID = "adityajn105/flickr8k"
DATASET_DIR = "flickr8k.zip"


def validate_api_credentials():
    """Validate Kaggle API user credentials. 
    """
    msg = ("In order to use the Kaggle’s public API, you must first \n"
           "authenticate using an API token. Please go to the \"Account\"\n"
           "tab at https://www.kaggle.com/account and click on \n"
           "\"Create New API Token\".\n"
           "\n"
           "Ensure kaggle.json is in the location ~/.kaggle/kaggle.json \n"
           "to use the API.")
    print(msg)

    while True:
        response = input('Downloaded API key? Continue [YyNn]: ')
        response = response.lower().strip()

        if response == 'y':
            try:
                json_path = Path.home() / '.kaggle' / 'kaggle.json'
                with open(json_path, 'r') as file:
                    credentials = json.load(file)
                    username = credentials['username']
                    key = credentials['key']
                    return
            except:
                print(("Not able to retrieve Kaggle API credentials. "
                       "Ensure kaggle.json \n"
                       "is in the location ~/.kaggle/kaggle.json to use "
                       "the API. \n"))
                sys.exit()
        elif response == 'n':
            sys.exit()


def download_and_extract(dataset_id, dataset_dir):
    """Downloads Kaggle dataset with identifier `dataset_id`.

    Arguments:
    ----------
        dataset_id (str):
            Dataset Identifier.
        dataset_dir (str):
            Name of downloaded data zip file from Kaggle.
    """
    # Download flickr8k data from Kaggle using Kaggle API.
    subprocess.run(f"kaggle datasets download -d {dataset_id}".split(),
        check=True)

    source = pathfinder.get('storyteller', 'search')
    dest_dir = pathfinder.get('storyteller', 'assets', 'data')

    # Unzip downloaded data directory.
    _zip = zipfile.ZipFile(dataset_dir)
    _zip.extractall()
    _zip.close()

    # Move downloaded flickr8k data to storyteller/assets/data.
    shutil.copytree(str(source / 'Images'), str(dest_dir / 'images'),
                    dirs_exist_ok=True)
    shutil.move(str(source / 'captions.txt'), str(dest_dir))

    # Remove copied Images directory from source.
    remove(source / 'Images', Path(dataset_dir))

    return


def split_data(dir, train_size):
    """Splits data into train and validation sets.

    Arguments:
    ----------
        dir (pathlib.Path):
            Path to images dir.
        train_size (float):
            Percentage of files in train set.

    Returns:
    --------
        train_images, val_images (tuple):
            List of images belonging to train and validation sets
            respectively.
    """
    images = sorted(list(dir.iterdir()))
    n_train = int(train_size * len(images))
    train_images, val_images = images[:n_train], images[n_train:]

    return train_images, val_images


def move_images(dir, train_images, val_images):
    """Copy images in `dir` into train and validation dirs.
    Original dir is deleted.

    Arguments:
    ----------
        dir (pathlib.Path):
            Path to images dir.
        train_images (list):
            List of image file names in trianing set.
        val_images (list):
            List of image file names in validation set.
    """
    train_dir, val_dir = Path(dir).parent / 'train', Path(dir).parent / 'val'

    train_dir.mkdir(exist_ok=True)
    val_dir.mkdir(exist_ok=True)

    for img in train_images:
        shutil.copy(img, train_dir / img.name)

    for img in val_images:
        shutil.copy(img, val_dir / img.name)


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
    val_images = set([image_path.name for image_path in val_images])
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

    with open(Path(file).parent / 'train_captions.json', 'w') as fileobj:
        json_contents = {
            'dataset': 'flickr8k',
            'contents': train_captions
        }
        json.dump(json_contents, fileobj, indent=4)

    with open(Path(file).parent /'val_captions.json', 'w') as fileobj:
        json_contents = {
            'dataset': 'flickr8k',
            'contents': val_captions
        }
        json.dump(json_contents, fileobj, indent=4)


def remove(dir, file):
    """Remove redundant files/dirs.

    Arguments:
    ----------
        dir (pathlib.Path):
            Path to images dir.
        file (pathlib.Path):
            Path to file containing captions.   
    """
    if dir is not None:
        shutil.rmtree(dir)

    if file is not None:
        file.unlink()
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download and organize data directory.')
    parser.add_argument('--train_size', dest='train_size', type=float,
                        default=0.8, help='Percentage of files in train-set')
    args = parser.parse_args()

    imgs_dir = pathfinder.get('storyteller', 'assets', 'data', 'images')
    captions_file = pathfinder.get('storyteller', 'assets', 'data', 'captions.txt')

    # Validate Kaggle API Credentials
    validate_api_credentials()

    # Download Kaggle dataset and place in storyteller/assets/data.
    download_and_extract(DATASET_ID, DATASET_DIR)

    # Split data into train and validation sets.
    train_imgs, val_imgs = split_data(imgs_dir, args.train_size)
    move_images(imgs_dir, train_imgs, val_imgs)
    txt_to_json(captions_file, val_imgs)
    remove(imgs_dir, captions_file)
