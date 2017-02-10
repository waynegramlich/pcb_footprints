# Copyright (c) 2011 by Wayne C. Gramlich.  All rights reserved.
#
# This code is to be released using an open source license (e.g
# GPL, ...)  I really do not care which one.

FOOTPRINT_DIRECTORIES :=	\
    IPC7351-Least		\
    IPC7351-Nominal		\
    IPC7351-Most
FOOTPRINT_MODULES := ${FOOTPRINT_DIRECTORIES:%=%.mod}
PDFS :=				\
    FreePCB_User_Guide.pdf	\
    IPC-7351BNamingConvention.pdf
FOOTPRINT_ZIP_FILES :=			\
    Makefile			\
    readme.txt			\
    fpl_convert.c

all: ${FOOTPRINT_MODULES} ${PDFS} fpl_convert.zip \
    README.html index.html index.pdf

${FOOTPRINT_MODULES}: ${FOOTPRINT_DIRECTORIES} fpl_convert
	./fpl_convert

fpl_convert: fpl_convert.c
	$(CC) -g -o $@ fpl_convert.c

clean:
	rm -rf ${FOOTPRINT_DIRECTORIES}
	rm -f fpl_convert

# Get naming conventions .pdf file:
IPC-7351BNamingConvention.pdf:
	wget http://landpatterns.ipc.org/IPC-7351BNamingConvention.pdf

# Unpack footprint .zip files:
IPC7351-Least: IPC7351-Least_v2.zip
	unzip IPC7351-Least_v2.zip
IPC7351-Nominal: IPC7351-Nominal_v2.zip
	unzip IPC7351-Nominal_v2.zip
IPC7351-Most: IPC7351-Most_v2.zip
	unzip IPC7351-Most_v2.zip
FreePCB_User_Guide.pdf: freepcb_1400_user_guide_pdf.zip
	unzip freepcb_1400_user_guide_pdf.zip
	touch $@

# Fetch footprint files from FREEPCB site:
IPC7351-Least_v2.zip:
	wget http://www.freepcb.com/downloads/IPC7351-Least_v2.zip
IPC7351-Nominal_v2.zip:
	wget http://www.freepcb.com/downloads/IPC7351-Nominal_v2.zip
IPC7351-Most_v2.zip:
	wget http://www.freepcb.com/downloads/IPC7351-Most_v2.zip
freepcb_1400_user_guide_pdf.zip:
	wget http://freepcb.com/downloads/freepcb_1400_user_guide_pdf.zip

fpl_convert.zip: ${ZIP_FILES}
	rm -f $@
	zip $@ ${ZIP_FILES}

index.html: README.html
	cp $< $@

# Rules:

%.html: %.md
	markdown $< > $@

%.pdf: %.html
	htmldoc --no-title --no-toc -f $@ $<
