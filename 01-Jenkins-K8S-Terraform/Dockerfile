FROM python:3.9

COPY . .

RUN pip3 install Flask gunicorn requests pymongo

ENV TZ="Asia/Jerusalem"

EXPOSE 5000

ENTRYPOINT FLASK_APP=beyt_cafe.py flask run --host=0.0.0.0