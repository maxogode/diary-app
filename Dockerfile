FROM python:3.10-slim


WORKDIR /app


COPY requirements.txt .
COPY run.py .
COPY config.py .
COPY app/ ./app


RUN pip install --upgrade pip
RUN pip install -r requirements.txt


ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development


EXPOSE 5000


CMD ["flask", "run"]
