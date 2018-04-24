FROM openmatchmaking/docker-base-python-image:3.6
RUN apt-get update && apt-get -y install make

COPY requirements-dev.txt /requirements-dev.txt
RUN pip install -r requirements-dev.txt

COPY ./ /app
WORKDIR /app