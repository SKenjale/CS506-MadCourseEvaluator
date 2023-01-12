FROM python:3.8.12-buster AS base

RUN pip install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

COPY . /app


EXPOSE 86
WORKDIR /app
ENTRYPOINT FLASK_APP=/backend_v1.py FLASK_ENV=development flask run -h 0.0.0.0 -p 5000