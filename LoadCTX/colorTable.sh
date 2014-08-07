#!/bin/bash

#Linux bash script for creation of GSI color table for Slicer

{
	echo "# GSI ColorTable"
	echo "#Begin table data:"
} > GSIStandard.txt

for i in {1..199}
do
	echo "${i} 20% 15 0 255 51" >> GSIStandard.txt
done

for i in {200..399}
do
	echo "${i} 40% 0 240 255 51" >> GSIStandard.txt
done

for i in {400..599}
do
	echo "${i} 60% 5 128 0 51" >> GSIStandard.txt
done

for i in {600..799}
do
	echo "${i} 80% 255 255 0 51" >> GSIStandard.txt
done

for i in {800..949}
do
	echo "${i} 80% 255 255 0 51" >> GSIStandard.txt
done

for i in {950..1049}
do
	echo "${i} 95% 255 0 0 51" >> GSIStandard.txt
done

for i in {1050..1060}
do
	echo "${i} 105% 255 0 255 51" >> GSIStandard.txt
done

echo "#EOF" >> GSIStandard.txt