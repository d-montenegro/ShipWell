FROM python:3.7-alpine
ENV PYTHONUNBUFFERED 1

WORKDIR /src

COPY ./ship_well /src

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 80

CMD python manage.py runserver 0.0.0.0:80
