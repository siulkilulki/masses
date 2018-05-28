#!/usr/bin/env bash

split_data() {
    split -l $[ $(wc -l "$1" | cut -d" " -f1) * 1 / 5 ] "$1" part- -d
    mv part-00 "$1_test.txt"
    mv part-01 "$1_dev.txt"
    cat part-0* > "$1_train.txt" && rm part-0* $1
}

grep '__label__yes' "$1"  > yes.txt
grep '__label__no'  "$1"  > no.txt
split_data yes.txt
split_data no.txt
cat yes.txt_train.txt no.txt_train.txt | shuf > train.txt
cat yes.txt_test.txt  no.txt_test.txt  | shuf > test.txt
cat yes.txt_dev.txt   no.txt_dev.txt   | shuf > dev.txt

diff <(sort "$1") <(cat train.txt test.txt dev.txt | sort)
rm yes.txt* no.txt*
