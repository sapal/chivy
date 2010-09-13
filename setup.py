# coding=utf-8
from setuptools import setup, find_packages
from sources.config import Config as config
import os

def allDir(dirName):
    return [ dirName+"/"+f for f in os.listdir(dirName) ] 

def translation(t):
    s = 'translations/{0}/LC_MESSAGES'.format(t)
    return (s, [s+'/base.mo'])

def addTranslations():
    return [ translation(t) for t in ("en_GB","pl_PL") ] + [("translations", ["translations/base.pot"])]

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
                ('levels', allDir('levels')) ] + addTranslations(),
    py_modules = ['chivy']

)
