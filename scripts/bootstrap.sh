#Author: Richard Torenvliet
#Github alias: icyrizard

#Set Script Name variable
SCRIPT=`basename ${BASH_SOURCE[0]}`

function HELP {
    echo "Basic usage: ./$SCRIPT <name_of_container>"
    echo "See makefile in root directory for more information"
}

#Check the number of arguments. If none are passed, print help and exit.
NUMARGS=$#
if [ $NUMARGS -eq 0 ]; then
    HELP
    exit 1
fi

VATICNAME=$1

# set names of the right env variables
USER=`echo ${VATICNAME^^}`_MYSQL_1_ENV_MYSQL_USER
PASS=`echo ${VATICNAME^^}`_MYSQL_1_ENV_MYSQL_PASS
HOST=`echo ${VATICNAME^^}`_MYSQL_1_PORT_3306_TCP_ADDR

# get env variables
MYSQL_USER=`env | grep $USER | awk '{split($0, str,"="); print str[2]}'`
MYSQL_PASS=`env | grep $PASS | awk '{split($0, str,"="); print str[2]}'`
MYSQL_HOST=`env | grep $HOST | awk '{split($0, str,"="); print str[2]}'`

# create database, ignore the "database exists" error.
(echo "create database vatic" | mysql -u$MYSQL_USER \
                                      -p$MYSQL_PASS \
                                      -h$MYSQL_HOST)

bash -c "turkic setup --database"
