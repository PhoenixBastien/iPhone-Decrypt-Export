#!/bin/bash

# add bin dir to PATH
PATH=~/bin:$PATH
# run python decrypt script
python -u decrypt.py
# export messages to html
imessage-exporter -f html -c full -p ~/Library/SMS/sms.db -o ~/export