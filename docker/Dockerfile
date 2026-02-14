FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY --parents api assets latex renderer src templates main.py LICENSE ./

ENTRYPOINT ["python3", "main.py"]