#!coding:utf8
import sys

try:
    from setuptools import setup
except:
    from distutils.core import setup
VERSION = "1.0.0"


if __name__ == "__main__":
    with open('requirements.txt') as f:
        required = f.read().splitlines()
    setup(
        name="gmessage",
        version=VERSION,
        packages=['sdk'],
        url='http://github.com/GeeTeam/gm-python-sdk',
        license='',
        author='Geetest',
        author_email='admin@geetest.com',
        description='Gmessage Python SDK',
        install_requires=required,
    	)