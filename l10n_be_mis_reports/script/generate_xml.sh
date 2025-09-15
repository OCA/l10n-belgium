#!/bin/bash

set -eu

while getopts ":a:f:y:" flag;
do
	case "${flag}" in
		a) author=${OPTARG};;
		f) filename=${OPTARG};;
		y) year=${OPTARG};;
	esac
done

python generate_xml.py --filename="m${filename}-f" --author=$author --year=$year  data/m${filename}-f.json calc/22_19_m${filename}-f.json
python correct_xml.py ../data/mis_report_bs_m${filename}-f.xml
python correct_xml.py ../data/mis_report_pl_m${filename}-f.xml
