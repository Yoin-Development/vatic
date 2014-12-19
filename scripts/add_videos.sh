#!/bin/bash
#Author: Richard Torenvliet
#Github alias: icyrizard

LABELS="person head"
INPUT_DIR=data/
OUTPUT_DIR=extract
FIND_FORMAT=mp4

#Set Script Name variable
SCRIPT=`basename ${BASH_SOURCE[0]}`

#Help function
function HELP {
    echo -e \\n"Help documentation for ${SCRIPT}."\\n
    echo -e "Basic usage: ./$SCRIPT <vatic_image_name>" \\n
    echo -e "vatic_image_name is the name of the image, see fig.yml"
    echo "Command line switches are optional. The following switches are
    recognized."
    echo "-i --Set input dir. default: $INPUT_DIR."
    echo "-o --Set output dir. default: $OUTPUT_DIR."
    echo "-f --Set extension to find {mp4, mpeg, etc..}. default: $FIND_FORMAT"
    echo "-h --Displays this help message. No further functions are
    #performed."
    echo -e "Example: ./$SCRIPT -i data/videos/ -o extract/ vatic"
    exit 1
}

#Check the number of arguments. If none are passed, print help and exit.
NUMARGS=$#
if [ $NUMARGS -eq 0 ]; then
    HELP
    exit 1
fi

while getopts :l:i:o:f:h FLAG; do
    case $FLAG in
        l)
            LABELS=$OPTARG
            ;;
        i)
            INPUT_DIR=$OPTARG
            ;;
        o)
            OUTPUT_DIR=$OPTARG
            ;;
        f)
            FIND_FORMAT=$OPTARG
            ;;
        h) #show help
            HELP
            ;;
        \?)
            echo -e \\n"Option -$OPTARG not allowed."
            HELP
            ;;
    esac
done

# shift ops, all optional args are now removed $1 will have to be the filename
shift $((OPTIND-1))

VATICNAME=$1
COUNTER=0

for i in `find $INPUT_DIR -name *.$FIND_FORMAT`
do
    ID=`basename $i`
    VIDEO="/$i"

    EXTRACT="fig run $VATICNAME turkic extract $VIDEO /$OUTPUT_DIR/$ID"
    LOAD="fig run $VATICNAME turkic load $ID /$OUTPUT_DIR/$ID $LABELS --offline"

    echo $EXTRACT
    echo $LOAD
    let COUNTER=COUNTER+1

    bash -c "$EXTRACT"
    bash -c "$LOAD"
done

if [ $COUNTER -gt 0 ]
then
    bash -c "fig run $VATICNAME turkic publish --offline"
fi

