#!/bin/bash

#Linux bash script to convert .hed header to .nrrd header

# 2014 Kristjan Anderle

if [ $# -lt 1 -o $# -gt 1 ];
    then
    echo "Linux script convert TRiP98 header to nrrd";
    echo " ";
    echo "Usage:";
    echo "Parameter: <path to .hed file or directory>";
    echo " ";
    exit 1;
fi

INPUT=$1
#Function for conversion of header
function convertHeader {
	HEADERFILE=$1
	if [[ ! $HEADERFILE =~ \.hed$ ]];
	then
		echo "$HEADERFILE is not a .hed file!"
		exit 1
	else
		PREFIX=$(basename ${HEADERFILE%.hed})
		DIRNAME=$(dirname ${HEADERFILE})
		newHeader="${DIRNAME}/${PREFIX}.nrrd"
		#Remove old file
# 		rm $newHeader
		SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
		#Template
		TEMPLATE=${SCRIPTDIR}/headerTmp.nrrd
		#Read data from TRiP header
		TYPE=$(awk '{ if($1=="data_type") { if($2=="float") {print "float"} else {print "short"}}}' ${HEADERFILE})
		NUM_BYTES=$(awk '{ if($1=="num_bytes") { print $2}}' ${HEADERFILE})
		if [ "$NUM_BYTES" == "4" ]
		then
			if [ "$TYPE" == "float" ]
			then
				TYPE="double"
			elif [ "$TYPE" == "short" ]
			then
				TYPE="int"
			fi
		fi
		ENDIAN=$(awk '{ if($1=="byte_order") { if($2=="vms") {print "little"} else {print "big"}}}' ${HEADERFILE})
		DIMX=$(awk '{ if($1=="dimx") { print $2}}' ${HEADERFILE})
		DIMY=$(awk '{ if($1=="dimy") { print $2}}' ${HEADERFILE})
		DIMZ=$(awk '{ if($1=="dimz") { print $2}}' ${HEADERFILE})
		ORIGINX=$(awk '{ if($1=="xoffset") { print $2}}' ${HEADERFILE})
		ORIGINY=$(awk '{ if($1=="yoffset") { print $2}}' ${HEADERFILE})
		ORIGINZ=$(awk '{ if($1=="zoffset") { print $2}}' ${HEADERFILE})
		SPACINGX=$(awk '{ if($1=="pixel_size") { print $2}}' ${HEADERFILE})
		SPACINGZ=$(awk '{ if($1=="slice_distance") { print $2}}' ${HEADERFILE})
		ENCODING="raw"
		#FIND COMPLEMENTARY FILECUBE TO HEADER
		FLIST=$(ls ${DIRNAME}/${PREFIX}*)
		
		for iFILE in $FLIST
		do
			
			if [[ ! $iFILE =~ \.hed$ ]] && [[ ! $iFILE =~ \.nrrd$ ]] && [[ ! $iFILE =~ \~$ ]];
			then
				EXT=${iFILE##*.}
				PRENAME=$(basename ${iFILE%.$EXT})
				if [ "$EXT" == "ctx" ] || [ "$EXT" == "dos" ] || [ "$EXT" == "cbt" ] || [ "$EXT" == "gz" ] || [ "$EXT" == "zip" ]
				then
					FILECUBE="${PRENAME}.${EXT}"
					if [ "$EXT" == "gz" ] ||  [ "$EXT" == "gz" ]
					then
						ENCODING="gzip"
					fi				
				fi
				
			fi
		done
		if [ ! -f ${DIRNAME}/${FILECUBE} ]
		then
			echo "No filecube at ${DIRNAME}/${FILECUBE}"
			echo "Check that there is ctx/dos/cbt/zip file with the same name as header!"
			return
		fi
# 		echo "$FILECUBE is with $TYPE $ENDIAN"
		#Change data in template
		sed -e s/#TYPE#/${TYPE}/g -e s/#ENDIAN#/${ENDIAN}/g -e s/#FILE#/$FILECUBE/g -e s/#ENCODING#/$ENCODING/g  \
		-e s/#DIMX#/${DIMX}/g -e s/#DIMX#/${DIMY}/g -e s/#DIMX#/${DIMZ}/g \
		-e s/#SPACINGX#/${SPACINGX}/g -e s/#SPACINGZ#/${SPACINGZ}/g \
		-e s/#ORIGINX#/${ORIGINX}/g -e s/#ORIGINY#/${ORIGINY}/g -e s/#ORIGINZ#/${ORIGINZ}/g \
		-e s/#DIMX#/${DIMX}/g -e s/#DIMY#/${DIMY}/g -e s/#DIMZ#/${DIMZ}/g \
		${TEMPLATE} > ${newHeader}
		echo "Converted: $HEADERFILE --> ${newHeader}"
	fi
	
}
if [ -f ${INPUT} ];
then
	convertHeader ${INPUT}
		
elif [ -d ${INPUT} ];
then
	FILELIST=$(ls ${INPUT})
	for FILE in $FILELIST
	do
		if [[ $FILE =~ \.hed$ ]];
		then
			convertHeader ${INPUT%/}/$FILE
		fi
	done
else
	echo "Invalid input. Please give header file or directory with headers."
fi
exit 1