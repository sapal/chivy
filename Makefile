translations/pl_PL/LC_MESSAGES/base.mo: translations/pl_PL.po
	msgfmt --output-file=translations/pl_PL/LC_MESSAGES/base.mo translations/pl_PL.po 

translations/en_GB/LC_MESSAGES/base.mo: translations/en_GB.po
	msgfmt --output-file=translations/en_GB/LC_MESSAGES/base.mo translations/en_GB.po 


all: translations/pl_PL/LC_MESSAGES/base.mo translations/en_GB/LC_MESSAGES/base.mo

.PHONY: all
