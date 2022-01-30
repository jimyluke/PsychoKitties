# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster
ADD . /psychokitties-backend
WORKDIR /psychokitties-backend
RUN pip3 install -r requirements.txt
RUN pip3 install pymysql
EXPOSE 5000
CMD [ "python3", "app.py" ]