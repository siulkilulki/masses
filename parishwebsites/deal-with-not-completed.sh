#!/usr/bin/env bash

./find-not-completed.sh > not-completed
# cat duplicate-data >> not-completed
#removes not truly finished in processed.txt
grep -v -f <(cat not-completed | sed -e 's@^@\t@' | sed -e 's@$@\$@') processed.txt | sponge processed.txt

#appends filenames from spider-commands.txt which are not in processed.txt
comm -13 <(cut -f2 processed.txt | sort -u) <(grep -o 'data/.*" 2>' spider-commands.txt | sed -Ee 's@data/|" 2>@@g' | sort) >> not-completed

sort -u not-completed | sponge not-completed

# remove data connected with not-completed e.g. logs/ data/

echo data directory file count: `ls -1 data | wc -l`
cd data && xargs rm -f < ../not-completed
cd ..
echo data directory file count: `ls -1 data | wc -l`
echo logs directory file count: `ls -1 logs | wc -l`
cd logs && xargs rm -f < ../not-completed
cd ..
echo logs directory file count: `ls -1 logs | wc -l`

grep -f <(cat not-completed | sed -e 's@^@"data/'@ | sed -e 's@$@"@') spider-commands.txt > spider-commands-add.txt
