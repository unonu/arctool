#!/bin/bash
cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
for i in $( ls *.ui); do
	fname=$( sed -e 's/\.ui$//' <<< "$i" )
	echo $fname
	/usr/bin/python3 -m PyQt5.uic.pyuic -i 0 $i -o "$fname.py"
done
