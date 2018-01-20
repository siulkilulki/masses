#!/usr/bin/env bash
cut -f3 ../scraper/extended.tsv | tail -n +2 | grep http | ./generate_spider_commands.sh | sort -u
