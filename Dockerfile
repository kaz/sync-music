FROM alpine:edge

RUN apk add ffmpeg python py3-pip gcc python3-dev libc-dev libffi-dev openssl-dev
RUN pip install google-music

WORKDIR /workdir
