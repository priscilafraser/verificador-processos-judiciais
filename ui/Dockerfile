FROM python:3.11-slim

# Diretório de trabalho dentro do container
WORKDIR /app

# Copia apenas o requirements da UI
COPY ui/requirements.txt ./requirements.txt

# Instala dependências do frontend
RUN pip install --no-cache-dir -r requirements.txt

# Copia apenas o código da UI
COPY ui/ ./ui

# Entra na pasta da UI
WORKDIR /app/ui

# Porta que o Railway vai injetar (ou usa 8501 localmente)
ENV PORT=8501

# Comando para rodar o Streamlit
CMD ["sh", "-c", "streamlit run app_interface.py --server.port=$PORT --server.address=0.0.0.0"]
