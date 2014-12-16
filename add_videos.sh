DIR=$1
LABELS="person head"
EXTRACT_DIR=/extract

for i in `find $DIR -name *.mp4`
do
        #echo $i
        ID=`echo $i | awk '{split($0, prefix,"."); print prefix[1]}' | \
            cut -d "/" -f2`
        VIDEO="/$i"
        EXTRACT="fig run vatic turkic extract $VIDEO $EXTRACT_DIR/$ID"
        LOAD="fig run vatic turkic load $ID $EXTRACT_DIR/$ID $LABELS --offline"
        bash -c "$EXTRACT"
        bash -c "$LOAD"
done

bash -c "fig run vatic turkic publish --offline"
