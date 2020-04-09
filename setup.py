import sys
import os
from setuptools import setup, find_packages

req_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "requirements.txt")
with open(req_path) as f:
    reqs = f.read().splitlines()


setup(name="skyway",
      version="0.0.1",
      author="Jamison Polackwich",
      author_email='',
      description="Python API for making OSM queries",
      url="",
      license="MIT",
      packages=find_packages(exclude=['docs', 'tests']),
      install_require=reqs
      )

