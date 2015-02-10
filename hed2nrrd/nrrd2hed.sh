#!/bin/bash

#Linux bash script to convert .nhdr header to .nrrd header

# 2014 Kristjan Anderle

if [ $# -lt 2 -o $# -gt 2 ];
    then
    echo "Linux script to convert nhrd header to TRiP98 header";
    echo " ";
    echo "Input <directory> to change all .nhdr to .nhdr or path to single .nhdr <file>.";
    echo " ";
    echo "Input <suffix> for appropriate cube generation (ctx, dos, cbt...)";
    echo "";
    exit 1;
fi

INPUT=$1
#Function for conversion of header
function convertHeader {
	HEADERFILE=$1
	SUFFIX=$2
	if [[ ! $HEADERFILE =~ \.nhdr$ ]] && [[ ! $HEADERFILE =~ \.nrrd$ ]];
	then
		echo "$HEADERFILE is not a .nhdr file!"
		return
	else
		DIRNAME=$(dirname ${HEADERFILE})
		if [[ $HEADERFILE =~ \.nhdr$ ]];
		then		
			PREFIX=$(basename ${HEADERFILE%.nhdr})
			oldHeader="${DIRNAME}/${PREFIX}_old.nhdr"
		elif [[ $HEADERFILE =~ \.nrrd$ ]];
		then
			PREFIX=$(basename ${HEADERFILE%.nrrd})
			oldHeader="${DIRNAME}/${PREFIX}_old.nrrd"
		fi
		cp $HEADERFILE $oldHeader
		
		newHeader="${DIRNAME}/${PREFIX}.hed"
		
		FLIST=$(awk '{ if($2=="file:") { print $3}}' ${HEADERFILE})
		if [ ! $FLIST ]
		then
			echo "No raw file, cannot convert to .hed"
			return
		fi
		#Remove old file
# 		rm $newHeader
		SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
		#Template
		TEMPLATE=${SCRIPTDIR}/headerTmp.hed
		#Read data from nhdr header
		DATATYPE=$(awk '{ if($1=="type:") { print $2}}' ${HEADERFILE})

		if [ "$DATATYPE" = "float" ] || [ "$DATATYPE" = "double" ]
		then
			TYPE="float"
			if [ "$DATATYPE" = "double" ]
			then
				NUM_BYTES="8"
			else
				NUM_BYTES="4"
			fi
		elif [ "$DATATYPE" = "int" ] || [ "$DATATYPE" = "short" ]
		then
			TYPE="integer"
			if [ "$DATATYPE" = "int" ]
			then
				NUM_BYTES="4"
			else
				NUM_BYTES="2"
			fi
		else
			echo "Unknow data type: ${DATATYPE}"
			return
		fi

		ENDIAN=$(awk '{ if($1=="endian:") { if($2=="little") {print "vms"} else {print "aix"}}}' ${HEADERFILE})
		DIMX=$(awk '{ if($1=="sizes:") { print $2}}' ${HEADERFILE})
		DIMY=$(awk '{ if($1=="sizes:") { print $3}}' ${HEADERFILE})
		DIMZ=$(awk '{ if($1=="sizes:") { print $4}}' ${HEADERFILE})
		ORIGINS=$(awk '{ if($2=="origin:") { print $3}}' ${HEADERFILE})
		ORIGINS=${ORIGINS#(}
		ORIGINS=${ORIGINS%)}
		ORIGINX=${ORIGINS%%,*}
		ORIGINS=${ORIGINS#$ORIGINX,}
		ORIGINY=${ORIGINS%%,*}
		ORIGINZ=${ORIGINS#$ORIGINY,}	

		SPACINGX_TMP=$(awk '{ if($2=="directions:") { print $3}}' ${HEADERFILE})
		SPACINGX=${SPACINGX_TMP#(}
		SPACINGX=${SPACINGX%%,*}
		SPACINGY_TMP=$(awk '{ if($2=="directions:") { print $4}}' ${HEADERFILE})
		SPACINGY=${SPACINGY_TMP#(*,}
		SPACINGY=${SPACINGX%,*)}
		SPACINGZ_TMP=$(awk '{ if($2=="directions:") { print $5}}' ${HEADERFILE})
		SPACINGZ=${SPACINGZ_TMP#(*,*,}
		SPACINGZ=${SPACINGZ%)}

		
		if [ ! "$SPACINGX" = "$SPACINGY" ]
		then
			echo "Spacing X and Y must be the same."
			return
		fi
		FLIST=$(awk '{ if($2=="file:") { print $3}}' ${HEADERFILE})
		if [ "$FLIST" = "LIST" ]
		then
			echo "Can't transform LIST"
			return
		fi

		#Rounding
		ORIGINX=$(echo $ORIGINX | awk  '{ rounded = sprintf("%.0f", $1); print rounded }')
		ORIGINY=$(echo $ORIGINY | awk  '{ rounded = sprintf("%.0f", $1); print rounded }')
		ORIGINZ=$(echo $ORIGINZ | awk  '{ rounded = sprintf("%.0f", $1); print rounded }')
		SPACINGX=$(echo $SPACINGX | awk  '{ rounded = sprintf("%.6f", $1); print rounded }')
		SPACINGZ=$(echo $SPACINGZ | awk  '{ rounded = sprintf("%.6f", $1); print rounded }')


		ENCODING=$(awk '{ if($1=="encoding:") { print $2}}' ${HEADERFILE})
		if [ "$ENCODING" = "gzip" ]
		then
				gunzip ${DIRNAME}/$FLIST
				FLIST=${FLIST%%.gz}
				sed -e s/"gzip"/"raw"/g $oldHeader > $HEADERFILE
				cp $HEADERFILE $oldHeader
		fi		
			
		NEWFILE="$PREFIX.$SUFFIX"
		mv ${DIRNAME}/$FLIST ${DIRNAME}/$PREFIX.$SUFFIX
		sed -e s/$FLIST/$NEWFILE/g $oldHeader > $HEADERFILE
		rm $oldHeader

		PATIENTNAME=$PREFIX
		
# 		echo "$FILECUBE is with $TYPE $ENDIAN"
		#Change data in template
		sed -e s/#TYPE#/${TYPE}/g -e s/#ENDIAN#/${ENDIAN}/g  -e s/#PATIENTNAME#/${PATIENTNAME}/g \
		-e s/#DIMX#/${DIMX}/g -e s/#DIMX#/${DIMY}/g -e s/#DIMX#/${DIMZ}/g \
		-e s/#SPACINGX#/${SPACINGX}/g -e s/#SPACINGZ#/${SPACINGZ}/g -e s/#NUM_BYTES#/${NUM_BYTES}/g \
		-e s/#ORIGINX#/${ORIGINX}/g -e s/#ORIGINY#/${ORIGINY}/g -e s/#ORIGINZ#/${ORIGINZ}/g \
		-e s/#DIMX#/${DIMX}/g -e s/#DIMY#/${DIMY}/g -e s/#DIMZ#/${DIMZ}/g  \
		${TEMPLATE} > ${newHeader}
		echo "Converted: $HEADERFILE --> ${newHeader}"
	fi
	
}
if [ -f ${INPUT} ];
then
	convertHeader ${INPUT} $2
		
elif [ -d ${INPUT} ];
then
	FILELIST=$(ls ${INPUT})
	for FILE in $FILELIST
	do
		if [[ $FILE =~ \.nhdr$ ]] || [[ $FILE =~ \.nrrd$ ]];
		then
			convertHeader ${INPUT%/}/$FILE $2
		fi
	done
else
	echo "Invalid input. Please give header file or directory with headers."
fi
exit 1