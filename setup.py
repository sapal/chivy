# coding=utf-8
from setuptools import setup, find_packages
from sources.config import Config as config
import os

def allDir(dirName):
    return [ dirName+"/"+f for f in os.listdir(dirName) ] 

setup(
    name = config.title,
    version = config.version,
    packages = find_packages(),
    include_package_data = True,


    author = "Michał Sapalski",
    author_email = "sapalskimichal@gmail.com",
    description = "Simple game.",
    license = "?",
    keywords = "game",
    platforms = 'any',
    install_requires = ["rabbyt >= 0.8.1", "pyglet >= 1.1.2"],
    data_files = [ ('images', allDir("images")), 
                ('tiled', allDir('tiled')),
                ('fonts', allDir('fonts')),
                ('levels', allDir('levels')) ],
    py_modules = ['__main__']

)
