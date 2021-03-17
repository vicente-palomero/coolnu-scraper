#!/bin/bash

BASE_RANDOM=$((-1 * $RANDOM))

while getopts d:i: flag
do
  case "${flag}" in
    d) database=${OPTARG};;
    i) input=${OPTARG};;
  esac
done

# Create Properties table
echo "Creating database"
sqlite3 $database "CREATE TABLE IF NOT EXISTS properties (pid INTEGER PRIMARY KEY, name STRING)"
echo ${input}

grep -Po "'P[0-9]*': {'label': (\"[[:alpha:] \/']*\"|'[[:alpha:] \/]*'), 'values': {'(img|value|link|Q[0-9]*)': [^}]*}?}?" ${input} | sort | uniq | sort | cut -d "," -f 1 | uniq | sed  "s/: {'label'//" | tr -d "'" | tr -d '"' | while read -r line; do
  pid=$(echo ${line} | cut -d ":" -f1)
  name=$(echo ${line} | cut -d ":" -f2 | xargs)
  echo "INSERT INTO properties (pid,name) VALUES (${pid:1}, '${name}')"
  sqlite3 $database "INSERT INTO properties (pid,name) VALUES (${pid:1}, '${name}')"
done
echo "Created"

# Create content tables

sqlite3 $database "CREATE TABLE IF NOT EXISTS entities (id INTEGER PRIMARY KEY, qid INTEGER UNIQUE, name STRING, wikidata STRING)"
sqlite3 $database "CREATE TABLE IF NOT EXISTS properties_entities (id INTEGER PRIMARY KEY AUTOINCREMENT, qid INTEGER, pid INTEGER, value_id STRING, value_text STRING, UNIQUE(qid, pid, value_id, value_text))"

grep -Po "'qid':(.*?)(}}}}|{}})" ${input} | while read -r line; do
  QID=$(grep -Po "(?<='qid': 'Q)[0-9]*" <<< ${line})
  NAME=$(grep -Po "(?<='title': )(.*?)(?=,)" <<< ${line})
  HREF=$(grep -Po "(?<='href': )(.*?)(?=,)" <<< ${line})

  if [ -z ${QID} ]; then
    QID=$(( ${BASE_RANDOM} * ${RANDOM} ))
  fi
  echo "INSERT INTO entities (qid, name, wikidata) VALUES (${QID}, ${NAME}, ${HREF})"
  sqlite3 $database "INSERT INTO entities (qid, name, wikidata) VALUES(${QID}, ${NAME}, ${HREF})"

  grep -Po "(?<='data': {)(.*?)}}}" <<< ${line} | while read -r data; do
    grep -Po "'P[0-9]*': {(.*?)}}(?=(,|}))" <<< ${data} | while read -r property; do
      PID=$(grep -Po "(?<='P)[0-9]*(?=')" <<< ${property})
      LABEL=$(grep -Po "(?<='label': )(.*?)(?=,)" <<< ${property})
      grep -Po "(?<='values': )(.*?)(?=}$)" <<< ${property} | while read -r value; do
        grep -Po "'(.*?)': ('(.*?)'|\"(.*'.*?)\")" <<< ${value} | while read -r one; do
          KEY=$(echo ${one} | cut -d ":" -f1)
          TEXT=$(echo ${one} | cut -d ":" -f2-)
          echo "INSERT INTO properties_entities (qid, pid, value_id, value_text) VALUES (${QID}, ${PID}, ${KEY}, ${TEXT})"
          sqlite3 $database "INSERT INTO properties_entities (qid, pid, value_id, value_text) VALUES (${QID}, ${PID}, ${KEY}, ${TEXT})"
        done
      done
    done
  done
done

echo "Done."
