FROM python:3.8.2

EXPOSE 80

ENV PYTHONPATH "${PYTHONPATH}:/app"

WORKDIR /app

ADD . /app/

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD python -m app polling