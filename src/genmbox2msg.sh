#!/bin/bash
conf_file="conf/phishing.yaml"

MBOX_DIR=$(grep 'mboxdir' ${conf_file} | sed 's/^.*: //')
for f in ${MBOX_DIR}/*.mbox; do
    if [ -f "$f" ]; then
      python3 mbox2msg.py $f
    fi
done

