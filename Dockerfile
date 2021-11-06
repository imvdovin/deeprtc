FROM nvidia/cuda:11.4.0-base-ubuntu20.04

ENV DEBIAN_FRONTEND="noninteractive" TZ="Europe/Moscow"

RUN apt-get update -y && apt-get install -y --no-install-recommends build-essential gcc \
  libsndfile1 ffmpeg sox git

RUN apt purge python3 && apt install -y python3.9 python3-pip

ENV HOME="/app"

# set work directory
WORKDIR $HOME

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip3 install --upgrade pip

RUN pip3 install Cython
RUN pip3 install redis

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

# copy project
COPY . .
