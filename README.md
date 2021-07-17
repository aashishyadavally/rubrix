# AI Based Visual Search Engine

## Project Description
This project uses a combined similarity search based on criteria such as objects within an image, and text captions for an image to retrieve relevant images.

## Getting Started
This section describes the preqrequisites, and contains instructions, to get the project up and running.

### Setup

#### 1. Project Environment
This project can easily be set up with all the prerequisite packages by following these instructions:
  1. Install [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/) using the `conda_install.sh` file, with the command: `$ bash conda_install.sh`
  2. Create a conda environment from the included `environment.yml` file using the following command:
     
     `$ conda env create -f environment.yml`
  3. Activate the environment
     
     `$ conda activate storyteller`
  4. To install the package with setuptools extras, use the following command in the top-level directory containing the `setup.py` file:
     
     `$ pip install .`

#### 2. Data Assets
Once the prerequisites have been installed, follow these instructions to build the project:
  1. Navigate to `storyteller/search` directory.
  2. Run the bash script `setup.sh` with the following command: 
  
     `$ bash setup.sh` 
   
   This downloads the [flickr8k](https://www.kaggle.com/adityajn105/flickr8k?select=captions.txt) dataset using the Kaggle API and sets up an image/embedding index.
     
     
### Usage


## Contributing Guidelines
There are no specific guidelines for contributing, apart from a few general guidelines we tried to follow, such as:
* Code should follow PEP8 standards as closely as possible
* We use [Google-Style docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) to document the Python modules in this project.

If you see something that could be improved, send a pull request! 
We are always happy to look at improvements, to ensure that `storyteller`, as a project, is the best version of itself. 

If you think something should be done differently (or is just-plain-broken), please create an issue.

## License
See the [LICENSE](https://github.com/aashishyadavally/storyteller/blob/master/LICENSE) file for more details.
