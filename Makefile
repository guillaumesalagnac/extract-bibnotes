
default: help


help:
	@echo 'usage:'
	@echo "'make all' to generate bibnotes for all entries in database.bib"
	@echo "make pick KEYS='Knu73 ASU86' to generate bibnotes for cherry-picked entries"
	@echo "add the 'view' target to open resulting pdf in Preview"
	@echo
	@echo  examples:
	@echo "    make pick KEYS='JRR14 Nak09 SSPx06' "
	@echo "    make clean pick KEYS=CHSC12 view "


view:
	open -a skim *.pdf

clean:
	rm -f bibannotation-* bibnotes*.pdf citations.tex
	latex-clean

##############################################
# all entries from database 

# usage: make all

all: bibnotes-all.pdf

bibnotes-all.pdf: bibnotes.tex 
	@./extract-bibannotations.py database.bib
	@echo '\\nocite{*}' > citations.tex
	@latex-clean --quiet
	latex-compile bibnotes.tex
	@mv bibnotes.pdf bibnotes-all.pdf

##############################################
# cherry-pick entries

# usage: make pick KEYS="Key1 Key2"

BIBANNOTATIONSFILES = $(patsubst %,bibannotation-%.tex,$(KEYS))

PDFNAME=$(shell echo $(KEYS) | sed 's/ //g')

NOCITE=$(shell echo $(KEYS) | sed 's/ /,/g')

# if the user fails to specify the 'KEYS' variable, then we abort.
ifndef KEYS
pick:help
	@exit 1
else
pick: bibnotes-$(PDFNAME).pdf
endif

bibnotes-$(PDFNAME).pdf: $(BIBANNOTATIONSFILES)
	@echo '\\nocite{'$(NOCITE)'}' > citations.tex
	latex-compile bibnotes.tex
	@mv bibnotes.pdf $@

bibannotation-%.tex: database.bib
	./extract-bibannotations.py database.bib $*
