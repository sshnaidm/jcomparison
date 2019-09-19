FROM python:3.6-alpine
MAINTAINER Sagi Shnaidman "einarum@gmail.com"
RUN apk update && \
    apk add --no-cache --virtual .build-deps python3-dev build-base libffi-dev openssl-dev linux-headers && \
    rm -rf /tmp/* && \
    rm -rf /var/cache/apk/* \
    rm -rf /root/.cache
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt && \
    apk del --no-cache --purge .build-deps linux-headers \
    rm -rf /tmp/* && \
    rm -rf /var/cache/apk/* \
    rm -rf /root/.cache
COPY . /app
ENTRYPOINT [ "python" ]
CMD [ "flask_comp.py" ]