FROM python:3.12-slim-bookworm

WORKDIR /app

EXPOSE 8501

COPY ./requirements.txt /app/requirements.txt

COPY ./src /app/src

COPY ./app.py /app/app.py

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
