#!/usr/bin/env bash

nfails=0
MAXFAILS=5

while :; do
    $( dirname $0 )/hwchecker.py -u kisel@corp.mail.ru -s imap.mail.ru --smtp smtp.mail.ru -p "$( cat ~/passw )" -e $HOME/work/ubuntu-ts/run_checker.sh -f ts2016dups@mail.ru --ok-folder ts2016dups@mail.ru/success --err-folder ts2016dups@mail.ru/failed -v
    if [[ $? -eq 0 ]]; then
        nfails=0
    else
        (( ++nfails ))
        if [[ $nfails -ge $MAXFAILS ]]; then
            echo "Too much time failed ($nfails). Exit"
            exit 1
        fi
    fi
    
    sleep 60
done
