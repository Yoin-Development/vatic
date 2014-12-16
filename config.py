from os import path, environ
import multiprocessing
import sys

signature   = "" # AWS secret access key
accesskey   = "" # AWS access key ID
sandbox     = False # if true, put on workersandbox.mturk.com
localhost   = "http://localhost:8181" # "http://localhost/" # your local host
database    = "mysql://admin:mypass@{link}/{db}"\
                    .format(link=environ.get('VATIC_MYSQL_1_PORT_3306_TCP_ADDR'),
                            db="vatic")
#database    = "mysql://root@localhost/vatic" # server://user:pass@localhost/dbname
geolocation = "" # api key for ipinfodb.com
maxobjects = 25;

# probably no need to mess below this line

print "config::::db ", localhost, database
print "env link", environ.get("VATIC_MYSQL_1_PORT_3306_TCP_ADDR")
processes = multiprocessing.cpu_count()

sys.path.append(path.dirname(path.abspath(__file__)))
