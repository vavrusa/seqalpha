#!/usr/bin/env bash
if [ $# -lt 1 ]; then
	echo "Usage: $0 <set>"
	exit 1
fi

set=$1
against="../gqclass-all.tsv"
echo "> filtering training set '$set' ($(cat $set/list|wc -l) PDBs)"
grep --file=${set}/list ${against} > ${set}.tsv 
