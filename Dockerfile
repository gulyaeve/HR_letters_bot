FROM python:3.10.5-slim-bullseye

WORKDIR /src

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .
RUN mkdir ./logs

ENTRYPOINT ["python", "app.py"]