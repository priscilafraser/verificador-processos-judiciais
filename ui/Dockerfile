FROM python:3.11-slim

# O WORKDIR está correto, definindo o diretório de trabalho dentro do container
WORKDIR /app/ui

# COPIA os arquivos do contexto (que AGORA é a pasta 'ui'). 
# O prefixo 'ui/' foi removido.
COPY requirements-ui.txt ./requirements.txt 
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante dos arquivos (app_interface.py) do contexto (ui/)
COPY . .

# Porta padrão do Streamlit
ENV PORT=8501

# Comando Padrão Streamlit
#CMD ["sh", "-c", "streamlit run app_interface.py --server.port=$PORT --server.address=0.0.0.0"]
CMD ["streamlit", "run", "app_interface.py", "--server.port=8501", "--server.address=0.0.0.0"]