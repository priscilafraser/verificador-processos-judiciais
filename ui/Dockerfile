FROM python:3.11-slim

# diretório de trabalho dentro do container
WORKDIR /app/ui

# copia somente os arquivos da UI
COPY ui/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ui/ .

# porta padrão do Streamlit (Railway vai injetar $PORT)
ENV PORT=8501

# comando para rodar a interface Streamlit
CMD ["sh", "-c", "streamlit run app_interface.py --server.port=$PORT --server.address=0.0.0.0"]
