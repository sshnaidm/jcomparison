FROM python:3.6-alpine
MAINTAINER Sagi Shnaidman "einarum@gmail.com"
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY . /app
ENTRYPOINT [ "python" ]
CMD [ "flask_comp.py" ]