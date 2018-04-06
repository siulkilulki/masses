SHELL := /bin/bash
PREPARE_ENVIRONMENT := $(shell ./prepare-environment.sh > /tmp/makeenv)
include /tmp/makeenv
JOBS := 6

.PHONY: all update data clean clean-data

all: data

data: parishwebsites/spider-commands.txt
	cd parishwebsites && parallel --jobs $(JOBS) < spider-commands.txt 2> crawler-log.txt

parishwebsites/spider-commands.txt: parishes-with-urls.tsv
	cut -f3 $< | tail -n +2 | grep http | parishwebsites/generate_spider_commands.sh | sort -u > $@

parishes-with-urls.tsv: apikey.txt parishes-deon.tsv scraper/get_parishes_urls.py
	scraper/get_parishes_urls.py -a $< -p $(word 2,$^) >> $@ 2> get-parishes-urls.log

parishes-deon.tsv: scraper/crawl_deon.py
	scraper/crawl_deon.py > $@ 2> crawl-deon.log

update: environment.yml
	conda env update -f $<

clean:
	rm -rf parishes-deon.tsv parishes-with-urls.tsv spider-commands.txt

clean-data:
	rm -rf parishwebsites/{data,processed.txt,crawler-log.txt}
