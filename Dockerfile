FROM python:3.12

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY .env ./

COPY . .

EXPOSE 8000

# Creacion del env
RUN python -m venv env
RUN /bin/bash -c "source env/bin/activate"

CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8000"]

