FROM python:3.7-alpine
ENV PYTHONUNBUFFERED 1

# Download git and clone mock-weather-api and install its deps
RUN apk update && apk add git
RUN git clone https://github.com/otterlogic/mock-weather-api /mock
WORKDIR /mock
RUN pip install -r requirements.txt

# Install ship_well
WORKDIR /src
COPY ./ship_well /src
RUN pip install --trusted-host pypi.python.org -r average_temperature/requirements.txt
EXPOSE 80

CMD FLASK_APP=/mock/app.py flask run -h 0.0.0.0 -p 5000 & python manage.py runserver 0.0.0.0:80
