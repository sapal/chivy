
VERSION=$(shell sed -n 's/[ ]*version *= *"\(.*\)"/\1/p' chivySources/config.py)

SOURCES=$(shell find chivySources -name '*.py')
DATA=$(shell find images tiled fonts levels)
I18N=translations/pl_PL/LC_MESSAGES/base.mo translations/en_GB/LC_MESSAGES/base.mo
DEB=$(shell find deb/usr -type f)
DEBVERSION=2
DEBFILES=deb/DEBIAN/control deb/usr/share/applications/chivy.desktop
HTML=$(shell find html)

all: dist/Chivy-${VERSION}-py2.6.egg dist/Chivy_${VERSION}-${DEBVERSION}_all.deb pl en
	
translations/pl_PL/LC_MESSAGES/base.mo: translations/pl_PL.po
	msgfmt --output-file=translations/pl_PL/LC_MESSAGES/base.mo translations/pl_PL.po 

translations/en_GB/LC_MESSAGES/base.mo: translations/en_GB.po
	msgfmt --output-file=translations/en_GB/LC_MESSAGES/base.mo translations/en_GB.po 

man/man6/chivy.6.gz: man/man6/chivy.txt
	txt2man -t chivy -s 6 -B chivy man/man6/chivy.txt > man/man6/chivy.6
	gzip --best -f man/man6/chivy.6

html/%.pl.html:html/template.html html/%.pl.content html/%.pl.title html/%.pl.lang html/generateHtml.py
	python html/generateHtml.py html/template.html html/menu.pl $@

html/%.en.html:html/template.html html/%.en.content html/%.en.title html/%.pl.lang html/generateHtml.py
	python html/generateHtml.py html/template.html html/menu.en $@

pl:html/mainPage.pl.html html/controls.pl.html html/installing.pl.html

en:html/mainPage.en.html html/controls.en.html html/installing.en.html

images/icon.png: images/icon.svg
	rsvg-convert images/icon.svg -o images/icon.png

dist/Chivy-${VERSION}-py2.6.egg: setup.py chivy.py ${SOURCES} ${DATA} images/icon.png ${I18N}
	python2.6 setup.py bdist_egg

dist/Chivy_${VERSION}-${DEBVERSION}_all.deb: chivy.py ${SOURCES} ${DATA} man/man6/chivy.6.gz ${DEBFILES} ${DEB} images/icon.png ${I18N}
	mkdir -p deb/usr/share/games/Chivy/
	mkdir -p deb/usr/share/man/man6/
	mkdir -p deb/usr/share/app-install/icons/
	mkdir -p deb/usr/share/pixmaps
	cp --preserve chivy.py chivySources images translations tiled levels fonts -R deb/usr/share/games/Chivy/
	cp --preserve man/man6/chivy.6.gz deb/usr/share/man/man6/
	cp --preserve images/icon.svg deb/usr/share/app-install/icons/chivy.svg
	cp --preserve images/icon.png deb/usr/share/pixmaps/chivy.png
	@$(shell ./generateMd5Sums.bash)
	sed --in-place "s/Installed-Size:.*/Installed-Size: $(shell du deb/usr -s | cut -f 1)/" deb/DEBIAN/control
	fakeroot dpkg-deb -D --build deb dist/Chivy_${VERSION}-${DEBVERSION}_all.deb

clean:
	rm dist -r || true
	rm html/*.pl.html html/*.en.html || true
	cd deb/usr/share/games/Chivy/ && rm -r chivy.py chivySources fonts images levels tiled translations || true
.PHONY: all pl en clean
