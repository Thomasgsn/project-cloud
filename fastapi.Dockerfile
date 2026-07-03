FROM python:3.12-slim-bookworm

WORKDIR /app

EXPOSE 8000

COPY ./fastapi_requirements.txt /app/fastapi_requirements.txt

COPY ./src /app/src

RUN pip install --no-cache-dir -r fastapi_requirements.txt

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
