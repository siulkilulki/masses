#!/usr/bin/env bash
(grep -r "No space left on device" logs | sort -u | grep "^logs/.*:OSError" -o | sed -Ee 's@^logs/|:OSError$@@g' | sort -u &&\
     grep -r 'Received SIGTERM' logs/ | grep '^logs/.*:20' -o | sed -Ee 's@^logs/|:20$@@g' | sort -u &&\
 find data -empty -type f | sed -e 's@data/@@' | sort
) | sort -u
