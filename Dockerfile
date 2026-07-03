FROM python:3.14-slim-bookworm

EXPOSE 8501

COPY ./requirements.txt .

COPY ./src ./src

COPY ./app.py .

RUN pip install -r requirements.txt

ENTRYPOINT streamlit run app.py --server.port 8501 --server.address 0.0.0.0