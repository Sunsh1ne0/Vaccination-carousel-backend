FROM python:3.12.1

RUN apt update && apt install -y python3-pip
RUN pip3 install FastAPI uvicorn PyYAML psycopg2
EXPOSE 8000
COPY . .
RUN mkdir -p /home/ubuntu/web/carousel_backend
CMD python3 main.py