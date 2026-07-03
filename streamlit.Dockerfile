FROM python:3.12-slim-bookworm

EXPOSE 8501

COPY ./streamlit_requirements.txt .

COPY ./src/config.py ./src/config.py

COPY ./src/document_store.py ./src/document_store.py

COPY ./src/rag_pipeline.py ./src/rag_pipeline.py

COPY ./app.py .

RUN pip install -r streamlit_requirements.txt

ENTRYPOINT streamlit run app.py --server.port 8501 --server.address 0.0.0.0