FROM python:alpine

RUN apk update && apk add git
RUN git clone https://github.com/xbgmsharp/trakt

WORKDIR /trakt

RUN pip install requests simplejson
