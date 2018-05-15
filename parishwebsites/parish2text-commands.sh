#!/usr/bin/env bash
for file in $1/*; do
    filename=`basename $file`
    echo "./parish2text.py < \"$file\" > \"text-data/$filename\" 2> \"text-data-logs/$filename\""
done
