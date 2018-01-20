#!/usr/bin/env bash

while IFS='$\n' read -r url; do
    echo "scrapy crawl parishes -a url=\"$url\" -t jsonlines -o  data/`echo "$url" | sed -Ee 's@/|:@@g' | sed 's/^http//g' | sed 's/^www\.//g'`"
done
