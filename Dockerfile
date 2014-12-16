FROM debian:wheezy
MAINTAINER rtorenvliet@yoin-vision.com

RUN apt-get update \
&& apt-get install -y python-setuptools python-dev libavcodec-dev \
libavformat-dev libswscale-dev libjpeg62 libjpeg62-dev libfreetype6 \
libfreetype6-dev apache2 libapache2-mod-wsgi mysql-client \
libmysqlclient-dev gfortran python-pip ffmpeg

ADD requirements.txt /

RUN pip install -r /requirements.txt

ADD pyvision/ /pyvision
RUN (cd /pyvision; python setup.py install)
env PATH /pyvision:$PATH

ADD *.py /var/www/vatic/
ADD *.ttf /var/www/vatic/
ADD public/ /var/www/vatic/public
ADD apache_defaultfile /etc/apache2/sites-enabled/000-default.conf

RUN cp /etc/apache2/mods-available/headers.load /etc/apache2/mods-enabled
RUN rm /etc/apache2/sites-enabled/000-default
RUN apache2ctl graceful

WORKDIR /var/www/vatic/
RUN turkic setup --public-symlink
RUN chown -R www-data:www-data /var/www/vatic

#RUN tail -f /var/log/apache2/access.log
CMD ["apache2ctl", "-e", "debug", "-D", "FOREGROUND"]

#["service", "apache2", "start"]

EXPOSE 80
