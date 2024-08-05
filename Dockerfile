FROM python:3.12.1

RUN apt update && apt install -y python3-pip
RUN pip3 install FastAPI uvicorn PyYAML
EXPOSE 3000
COPY . .
CMD python3 main.py