SHELL := /bin/bash
PREPARE_ENVIRONMENT := $(shell ./prepare-environment.sh > /tmp/makeenv)
include /tmp/makeenv


.PHONY: all clean

all: parishes-deon.txt

parishes-deon.tsv:
	./crawl_deon.py > $@

annotated-filtered.tsv: annotated-warszawa.tsv annotated-poznan.tsv
	cat $< <(tail -n +2 $(word 2, $^)) > tmp_
	./intersect_parishes.py -a tmp_ > $@

annotated-warszawa.tsv:
	./crawl_warszawa.py > $@ 2> error_warszawa

annotated-poznan.tsv:
	./crawl_poznan.py > $@ 2> error_poznan

clean:
	rm -rf parishes-deon.txt

update:
	conda env update -f ../environment.yml
