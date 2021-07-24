"""
A setuptools based setup module.
References: https://github.com/pypa/sampleproject
"""
import os
from setuptools import setup, find_packages


repo_dir = os.path.abspath(__file__)
# Long description is just the contents of README.md
long_description = 'Read README.md for long description'

setup(
	# Users can install the project with the following command:
	#		$ pip install toxcom
	#
	# It will live on PyPi at:
	#		https://pypi.org/project/toxcom/
	name='rubrix',
	# Versions should comply with PEP 440 : 
	# 		https://www.python.org/dev/peps/pep-0440/
	version='0.0.1-dev',
	# Packages can be manually mentioned, or `setuptools.find_packages`
	# can be used for this purpose.
	packages=find_packages(),
	description='AI Powered Image Search Engine',
	long_description=long_description,
	# Corresponds to the Home Page of the metadata field
	url='https://github.com/aashishyadavally/rubrix',
	# Name and email addresses of project owners.
	author='Aashish Yadavally',
	author_email='aashish.yadavally1995@gmail.com',
	classifiers=[
		'Intended Audience :: Science/Research',
		'Topic :: Scientific/Engineering :: Computer Vision :: Natural Language Processing',

		'Programming Language :: Python :: 3.8',
	],
	python_requires='>=3.6',
	)
