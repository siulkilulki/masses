#!/usr/bin/env bash

while IFS='$\n' read -r url; do
    filename="`echo "$url" | sed -Ee 's@/|:|\?|\!|\*|\(|\)|=|'"'"'|\+|;|,|\@|#|\[|\]|\$|&@@g' | sed 's/^http//g' | sed 's/^www\.//g'`"
    echo "scrapy crawl parishes -a url=\"$url\" -a filename=\"$filename\"  -t jsonlines -o \"data/$filename\" 2> \"logs/$filename\" "
done
