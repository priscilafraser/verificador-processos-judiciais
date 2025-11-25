FROM python:3.11-slim

# diretório de trabalho dentro do container
WORKDIR /app/ui

# copia os arquivos de dependência
COPY ui/requirements-ui.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante dos arquivos da UI (app_interface.py)
COPY ui/. .

# porta padrão do Streamlit (Railway vai injetar $PORT)
ENV PORT=8501

# comando para rodar a interface Streamlit
CMD ["sh", "-c", "streamlit run app_interface.py --server.port=$PORT --server.address=0.0.0.0"]