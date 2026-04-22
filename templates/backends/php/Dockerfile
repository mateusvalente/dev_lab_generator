FROM php:8.3-fpm

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl nginx \
    && rm -rf /var/lib/apt/lists/* \
    && docker-php-ext-install pdo_mysql

COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY start-backend.sh /usr/local/bin/start-backend.sh
RUN sed -i 's/\r$//' /usr/local/bin/start-backend.sh \
    && chmod +x /usr/local/bin/start-backend.sh \
    && mkdir -p /run/php /var/lib/nginx /var/log/nginx

WORKDIR /app
CMD ["sh", "/usr/local/bin/start-backend.sh"]
