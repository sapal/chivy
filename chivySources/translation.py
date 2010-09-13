# coding=utf-8
import gettext as Gettext
import locale
import os
from config import Config as config

APP_NAME = "base"
langs = [config.locale]
lc, encoding = locale.getdefaultlocale()
if (lc):
    langs += [lc]
language = os.environ.get('LANGUAGE', None)
if (language):
    langs += language.split(":")
langs += ["pl_PL"]

Gettext.bindtextdomain(APP_NAME, config.translationsDir)
Gettext.textdomain(APP_NAME)

lang = Gettext.translation(APP_NAME, config.translationsDir, languages=langs, fallback = True)
def gettext(*args, **kwargs):
    return unicode(lang.gettext(*args, **kwargs),"utf-8")
