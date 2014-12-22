FROM debian:wheezy
MAINTAINER rtorenvliet@yoin-vision.com

RUN apt-get update \
&& apt-get install -y python-setuptools python-dev libavcodec-dev \
libavformat-dev libswscale-dev libjpeg62 libjpeg62-dev libfreetype6 \
libfreetype6-dev apache2 libapache2-mod-wsgi mysql-client \
libmysqlclient-dev gfortran python-pip ffmpeg git

ADD requirements.txt /

RUN pip install -r /requirements.txt

RUN git clone --depth=1 https://github.com/cvondrick/turkic.git
RUN (cd /turkic; python setup.py install)
env PATH /turkic:$PATH

RUN git clone --depth=1 https://github.com/cvondrick/pyvision.git
RUN find /pyvision/ -name *.py \
        -exec sed -i -e 's/import Image/from PIL import Image/g' {} \;

RUN (cd /pyvision; python setup.py install)
env PATH /pyvision:$PATH

ADD *.py /var/www/vatic/
ADD plugins/ /var/www/vatic/plugins/
ADD *.ttf /var/www/vatic/
ADD public/ /var/www/vatic/public
ADD apache_defaultfile /etc/apache2/sites-enabled/000-default.conf

RUN cp /etc/apache2/mods-available/headers.load /etc/apache2/mods-enabled
RUN rm /etc/apache2/sites-enabled/000-default
RUN apache2ctl graceful

RUN ln -sf /dev/stdout /var/log/apache2/access.log
RUN ln -sf /dev/stderr /var/log/apache2/error.log

WORKDIR /var/www/vatic/
RUN turkic setup --public-symlink
RUN chown -R www-data:www-data /var/www/vatic

CMD ["apache2ctl", "-e", "debug", "-D", "FOREGROUND"]

EXPOSE 80
