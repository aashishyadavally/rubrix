<!--# AI Powered Visual Search Engine -->
<p align="center">
<img width="700" height="300" src="https://github.com/aashishyadavally/rubrix/blob/main/notebooks/images/cover.png">
</p>

# AI Powered Visual Search Engine
The main motivation behind building ``rubrix`` was to have a visual search engine completely powered by Artificial Intelligence, tying concepts within the fields of Natural Language Processing and Computer Vision, something we like to call "combined similarity search". Currently ``rubrix`` has two main functionalities:
- take in a user input describing an image and retrieve five images that fit that description (image search)
- take in a user uploaded image and retrieve five similar images (reverse-image search)

Please click [here](https://github.com/aashishyadavally/rubrix/wiki) to know more details about the architecture and how ``rubrix`` works!

## ``rubrix`` in Action

You can check out some of the images retrieved by ``rubrix`` for sample queries [here](https://github.com/aashishyadavally/rubrix/wiki/Query-Examples).

## Getting Started
This section describes the preqrequisites, and contains instructions, to get the project up and running.

### Setup 

#### 1. Project Environment
Currently, ``rubrix`` works flawlessly on Linux, and can be set up easily with all the prerequisite packages by following these instructions:
  1. Download appropriate version of [conda](https://repo.anaconda.com/miniconda/) for your machine.
  2. Install  it by running the `conda_install.sh` file, with the command:
     ```bash
     $ bash conda_install.sh
     ```
  3. Add `conda` to bash profile:
     ```bash
     $ source ~/.bashrc
     ```
  4. Navigate to ``rubrix/`` (top-level directory) and create a conda virtual environment with the included `environment.yml` file using the following command:
     
     ```bash
     $ conda env create -f environment.yml
     ```
  5. Activate the virtual environment with the following command:
     
     ```bash
     $ conda activate rubrix
     ```
  6. To install the package with setuptools extras, use the following command in ``rubrix/`` (top-level directory) containing the `setup.py` file:
     
     ```bash
     $ pip install .
     ```

#### 2A. Data Assets - Setup from Scratch
Once the prerequisites have been installed, follow these instructions to build the project:
  1. Navigate to `rubrix/index` directory.
  2. Run the bash script `setup.sh` with the following command: 
  
     ```bash
     $ bash setup.sh
     ``` 

What does this do?
1. Downloads flickr8k image/captions dataset.
2. Builds and sets up `darknet/` within `rubrix/index` to enable object detection with YOLOv4.
3. Creates `assets/index.json` file, which essentially is an inverse-image index mapping all the objects YOLOv4 was trained on, to the images containing them.
4. Creates `assets/imageEmbeddingLocations.json` file, which essentially maps all the images in the database to the sentence embedding vectors generated for each of the captions in the database.
5. Generates feature vectors describing all the images in the database and save it to `assets/descriptors` directory.


> **NOTE:** The above script can take between 1.5 - 2 hours to complete execution.

#### 2B. Data Assets - Quick Setup
1. Download data assets from [this](https://drive.google.com/file/d/1ZhGar-0OxdCikeWhDcsdm0Uov6qOto0S/view?usp=sharing) link.
2. Unzip and save the contents in ``rubrix/assets``.
3. All is left is to change the paths in ``rubrix/assets/index.json`` and ``rubrix/assets/imageEmbeddingLocations.json`` relative to the local machine. This can be done as follows:
   - Ensure corresponding virtual environment is active, or activate with the following command: 
     ```bash
     $ conda activate rubrix
     ```
   - Launch Python Interpretor in the terminal and run the following code snippet:
     ```python
     >>> from rubrix.utils import fix_paths_in_index
     >>> path_to_index = <absolute/path/to/rubrix/assets/index.json>
     >>> path_to_emb = <absolute/path/to/rubrix/assets/imageEmbeddingLocations.json>
     >>> fix_paths_in_index(path_to_index, path_to_emb)
     ```
 4. Navigate to ``rubrix/rubrix/index`` directory and run the following bash script:
    ```bash
    $ bash quick_setup.sh
    ```

### Usage

#### 1. As a package
With the completion of these steps, you should be able to use `rubrix`.

  - For image search, execute the `rubrix/query/query_by_text` method.
  - For reverse image search, execute the `rubrix/query/query_by_image_objects` method.

You can also follow a working example for this [here](https://github.com/aashishyadavally/rubrix/blob/main/notebooks/demo.ipynb).

#### 2. Web Application
An alternative is to use ``rubrix`` as an application on web browser. 

  - Navigate to ``rubrix/rubrix/web`` directory.
  - Enter the following cammand in the terminal to launch web application:
    ```bash
    $ python app.py
    ```

## Contributing Guidelines
There are no specific guidelines for contributing, apart from a few general guidelines we tried to follow, such as:
* Code should follow PEP8 standards as closely as possible
* We use [Google-Style docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) to document the Python modules in this project.

If you see something that could be improved, send a pull request! 
We are always happy to look at improvements, to ensure that `rubrix`, as a project, is the best version of itself. 

If you think something should be done differently (or is just-plain-broken), please create an issue.

## License
See the [LICENSE](https://github.com/aashishyadavally/storyteller/blob/master/LICENSE) file for more details.
