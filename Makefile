
VERSION=$(shell sed -n 's/[ ]*version *= *"\(.*\)"/\1/p' chivySources/config.py)

SOURCES=$(shell find chivySources -name '*.py')
DATA=$(shell find images tiled fonts levels)
I18N=translations/pl_PL/LC_MESSAGES/base.mo translations/en_GB/LC_MESSAGES/base.mo
DEBFILES=deb/DEBIAN/control deb/usr/games/chivy deb/usr/share/games/Chivy/chivy deb/usr/share/applications/chivy.desktop
HTML=$(shell find html)

translations/pl_PL/LC_MESSAGES/base.mo: translations/pl_PL.po
	msgfmt --output-file=translations/pl_PL/LC_MESSAGES/base.mo translations/pl_PL.po 

translations/en_GB/LC_MESSAGES/base.mo: translations/en_GB.po
	msgfmt --output-file=translations/en_GB/LC_MESSAGES/base.mo translations/en_GB.po 

man/man6/chivy.6.gz: man/man6/chivy.txt
	txt2man -t chivy man/man6/chivy.txt > man/man6/chivy.6
	gzip -f man/man6/chivy.6

html/mainPage.html:html/template.html html/mainPage.content html/mainPage.title
	python html/generateHtml.py html/template.html html/mainPage.html

html/controls.html:html/template.html html/controls.content html/controls.title
	python html/generateHtml.py html/template.html html/controls.html

html/installing.html:html/template.html html/installing.content html/installing.title
	python html/generateHtml.py html/template.html html/installing.html

images/icon.png: images/icon.svg
	rsvg-convert images/icon.svg -o images/icon.png

dist/Chivy-${VERSION}-py2.6.egg: setup.py chivy.py ${SOURCES} ${DATA} images/icon.png ${I18N}
	python setup.py bdist_egg

dist/Chivy_${VERSION}-1_all.deb: chivy.py ${SOURCES} ${DATA} man/man6/chivy.6.gz ${DEBFILES} images/icon.png ${I18N}
	mkdir -p deb/usr/share/games/Chivy/
	mkdir -p deb/usr/share/man/man6/
	#mkdir -p deb/usr/share/icons/hicolor/scalable/apps
	mkdir -p deb/usr/share/app-install/icons/
	mkdir -p deb/usr/share/pixmaps
	cp chivy.py chivySources images translations tiled levels fonts -R deb/usr/share/games/Chivy/
	cp man/man6/chivy.6.gz deb/usr/share/man/man6/
	#cp images/icon.svg deb/usr/share/icons/hicolor/scalable/apps/chivy.svg
	cp images/icon.svg deb/usr/share/app-install/icons/chivy.svg
	cp images/icon.png deb/usr/share/pixmaps/chivy.png
	fakeroot dpkg-deb --build deb dist/Chivy_${VERSION}-1_all.deb

all: dist/Chivy-${VERSION}-py2.6.egg dist/Chivy_${VERSION}-1_all.deb ${HTML}

.PHONY: all
