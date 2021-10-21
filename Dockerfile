FROM python:3.9

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