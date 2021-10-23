FROM python:3.9


RUN apt-get update -y && apt-get install -y --no-install-recommends build-essential gcc \
  libsndfile1 ffmpeg sox

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip

RUN pip install Cython
RUN pip install redis

COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .