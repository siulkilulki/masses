SHELL := /bin/bash
PREPARE_ENVIRONMENT := $(shell ./prepare-environment.sh > /tmp/makeenv)
include /tmp/makeenv
JOBS := 100

.PHONY: all update data clean clean-data clean-cache

all: data

parish2text: parishwebsites/parish2text.py parishwebsites/parish2text-commands.sh
	mkdir -p parishwebsites/{text-data,text-data-logs}
	cd parishwebsites && ./parish2text-commands.sh data > p2t-commands.txt && parallel --jobs -2 < p2t-commands.txt

data-add: parishwebsites/spider-commands-add.txt parishwebsites/domain-blacklist.txt parishwebsites/deal-with-not-completed.sh
	cd parishwebsites && ./deal-with-not-completed.sh
	cd parishwebsites && parallel --jobs $(JOBS) < spider-commands-add.txt

data: parishwebsites/spider-commands.txt parishwebsites/domain-blacklist.txt
	rm -f parishwebsites/*processed.txt
	cd parishwebsites && parallel --jobs $(JOBS) < spider-commands.txt

parishwebsites/spider-commands.txt: parishes-with-urls.tsv parishwebsites/domain-blacklist.txt
	cut -f3 $< | tail -n +2 | grep http | parishwebsites/generate_spider_commands.sh | sort -u | parishwebsites/remove_blacklisted.py $(word 2,$^) | parishwebsites/remove_duplicate_commands.py > $@

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

clean-cache:
	rm -rf parishwebsites/.scrapy/httpcache
