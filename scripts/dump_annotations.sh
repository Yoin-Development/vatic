#!/bin/bash
#Author: Richard Torenvliet
#Github alias: icyrizard

INPUT_DIR=data/
OUTPUT_DIR=data/annotations
FIND_FORMAT=mp4
OUTPUT_DIMS=1280x720

#Set Script Name variable
SCRIPT=`basename ${BASH_SOURCE[0]}`

#Help function
function HELP {
    echo -e \\n"Help documentation for ${SCRIPT}."\\n
    echo -e "Basic usage: ./$SCRIPT"\\n
    echo "Command line switches are optional. The following switches are
    recognized."
    echo "-d --Set output dimensions $OUTPUT_DIMS}."
    echo "-i --Set input dir. default: $INPUT_DIR."
    echo "-f --Set extension to find {mp4, mpeg, etc..}. default: $FIND_FORMAT"
    echo "-h --Displays this help message. No further functions are
    performed."
    echo -e "Example: ./$SCRIPT -d 1280x720 -i data/ "
    exit 1
}

#Check the number of arguments. If none are passed, print help and exit.
NUMARGS=$#
if [ $NUMARGS -eq 0 ]; then
    HELP
    exit 1
fi

while getopts :i:d:f:h FLAG; do
    case $FLAG in
        i)
            INPUT_DIR=$OPTARG
            ;;
        d)
            OUTPUT_DIMS=$OPTARG
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

for i in `find $INPUT_DIR -name *.$FIND_FORMAT`
do

    ID=`echo $i | awk '{split($0, str, "."); print str[1]}' | \
        cut -d "/" -f2`
    VIDEO="/$i"

    fig run vatic turkic dump $ID -o /$OUTPUT_DIR/$ID.txt --dimensions $OUTPUT_DIMS
done
