FROM python:3.8-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN rm -f requirements.txt

RUN mkdir /app/conf.d/
RUN mkdir /app/db.d/

COPY / /app/

ARG CONFIG_FILE
ARG SLEEP_TIME

CMD python ./main.py --config ${CONFIG_FILE} --sleep ${SLEEP_TIME}
