# Originally at
# https://github.com/jonathanheilmann/docker-httpd-alpine-rewrite/blob/master/Dockerfile

FROM httpd:2.4-alpine

RUN sed -i '/LoadModule rewrite_module/s/^#//g' /usr/local/apache2/conf/httpd.conf && \
    sed -i 's#AllowOverride [Nn]one#AllowOverride All#' /usr/local/apache2/conf/httpd.conf
