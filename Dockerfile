FROM python:3.8-alpine

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /app

CMD [ "python", "./app/main.py" ]
