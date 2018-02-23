#!/bin/bash

#Linux bash script to convert .hed header to .nrrd header

# 2014 Kristjan Anderle

if [ $# -lt 1 -o $# -gt 1 ];
    then
    echo "Linux script convert TRiP98 header to nrrd";
    echo " ";
    echo "Input <directory> to change all .hed to .nrrd or path to .hed <file>.";
    echo "";
    exit 1;
fi

INPUT=$1
#Function for conversion of header
function convertHeader {
	HEADERFILE=$1
	if [[ ! $HEADERFILE =~ \.hed$ ]];
	then
		echo "$HEADERFILE is not a .hed file!"
		return
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
			if [ "$TYPE" == "short" ]
			then
				TYPE="int"
			fi
		fi
		if [ "$NUM_BYTES" == "8" ]
		then
			if [ "$TYPE" == "float" ]
			then
				TYPE="double"
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
		#Vector field specification
		DIMENSIONS="3"
		DIMV=""
		SPACINGV=""
		DOMAINV=""
		VFILEX=""
		VFILEY=""
		VFILEZ=""
		#FIND COMPLEMENTARY FILECUBE TO HEADER
		FLIST=$(ls ${DIRNAME}/${PREFIX}.*)
		
		for iFILE in $FLIST
		do
			
			if [[ ! $iFILE =~ \.hed$ ]] && [[ ! $iFILE =~ \.nrrd$ ]] && [[ ! $iFILE =~ \~$ ]];
			then
				EXT=${iFILE##*.}
				PRENAME=$(basename ${iFILE%.$EXT})
				if [ "$EXT" == "ctx" ] || [ "$EXT" == "dos" ] || [ "$EXT" == "gz" ] || [ "$EXT" == "zip" ]
				then
					FILECUBE="${PRENAME}.${EXT}"
					if [ "$EXT" == "gz" ] ||  [ "$EXT" == "zip" ]
					then
						ENCODING="gzip"
					fi
					if [ ! -f ${DIRNAME}/${FILECUBE} ]
					then
						echo "No filecube at ${DIRNAME}/${FILECUBE}"
						echo "Check that there is ctx/dos/cbt/zip file with the same name as header!"
						return
					fi
				fi				
				#Check for cbt vectors
				if [ "$EXT" == "cbt" ] || [[ $PRENAME == *cbt* ]]
				then
					#Find out which component
					BASEVECTORNAME=$(basename ${iFILE})
					if [[ $BASEVECTORNAME == *_x.* ]]
					then
						VECTORNAME=${BASEVECTORNAME%_x.*}
						VECTOREXT=${BASEVECTORNAME##*_x.}
					elif [[ $BASEVECTORNAME == *_y.* ]]
					then
						VECTORNAME=${BASEVECTORNAME%_y.*}
						VECTOREXT=${BASEVECTORNAME##*_y.}
					elif [[ $BASEVECTORNAME == *_z.* ]]
					then
						VECTORNAME=${BASEVECTORNAME%_z.*}
						VECTOREXT=${BASEVECTORNAME##*_z.}
					else
						echo "No x, y or z component in vector field file:"
						echo "$BASEVECTORNAME"
						return
					fi
					FILECUBE="LIST"
					VFILEX="${VECTORNAME}_x.${VECTOREXT}"
					VFILEY="${VECTORNAME}_y.${VECTOREXT}"
					VFILEZ="${VECTORNAME}_z.${VECTOREXT}"
					DIMENSIONS="4"
					DIMV="3"
					SPACINGV="none"
					DOMAINV="vector"
				fi
			fi
		done
		
# 		echo "$FILECUBE is with $TYPE $ENDIAN"
		#Change data in template
		sed -e s/#TYPE#/${TYPE}/g -e s/#ENDIAN#/${ENDIAN}/g -e s/#FILE#/$FILECUBE/g -e s/#ENCODING#/$ENCODING/g  \
		-e s/#DIMX#/${DIMX}/g -e s/#DIMX#/${DIMY}/g -e s/#DIMX#/${DIMZ}/g \
		-e s/#SPACINGX#/${SPACINGX}/g -e s/#SPACINGZ#/${SPACINGZ}/g \
		-e s/#ORIGINX#/${ORIGINX}/g -e s/#ORIGINY#/${ORIGINY}/g -e s/#ORIGINZ#/${ORIGINZ}/g \
		-e s/#DIMX#/${DIMX}/g -e s/#DIMY#/${DIMY}/g -e s/#DIMZ#/${DIMZ}/g -e s/#DIMV#/${DIMV}/g \
		-e s/#VFILEX#/${VFILEX}/g -e s/#VFILEY#/${VFILEY}/g -e s/#VFILEZ#/${VFILEZ}/g  \
		-e s/#DIMENSIONS#/${DIMENSIONS}/g -e s/#SPACINGV#/${SPACINGV}/g -e s/#DOMAINV#/${DOMAINV}/g \
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