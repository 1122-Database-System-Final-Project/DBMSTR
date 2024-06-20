FROM python:3.9

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

ENV FLASK_APP=app2.py

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]