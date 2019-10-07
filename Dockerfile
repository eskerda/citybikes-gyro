FROM python:2.7-buster
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apt-get update && apt-get -y install git libgeos-dev
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT [ "/bin/sh" ]
CMD [ "worker.sh" ]