#!/bin/bash

FILE="out/tv_producers.json"

sqlite3 test.db "CREATE TABLE IF NOT EXISTS Properties (pid INTEGER PRIMARY KEY, name STRING)"

grep -Po "'P[0-9]*': {'label': (\"[[:alpha:] \/']*\"|'[[:alpha:] \/]*'), 'values': {'(img|value|link|Q[0-9]*)': [^}]*}?}?" ${FILE} | sort | uniq | sort | cut -d "," -f 1 | uniq | sed  "s/: {'label'//" | tr -d "'" | tr -d '"' | while read -r line; do
  pid=$(echo ${line} | cut -d ":" -f1)
  name=$(echo ${line} | cut -d ":" -f2 | xargs)
  sqlite3 test.db "INSERT INTO Properties (pid,name) VALUES (${pid:1}, '${name}')"
done
