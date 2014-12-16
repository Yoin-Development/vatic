#!/bin/bash
DIR=$1
OUTPUT=data/annotations

for i in `find $DIR -name *.mp4`
do
        ID=`echo $i | awk '{split($0, prefix,"."); print prefix[1]}' | \
            cut -d "/" -f2`
        VIDEO="/$i"
        echo $ID

        fig run vatic turkic dump $ID -o /$OUTPUT/$ID.txt --dimensions 1280x720
done
