FROM python:3.9

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

ENV FLASK_APP=app.py

EXPOSE 8000

CMD ["python", "app.py"]