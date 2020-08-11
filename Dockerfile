FROM python:3.7

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app

RUN mkdir /app/logs

CMD ["python", "-u", "delete-trello-archives.py"]
