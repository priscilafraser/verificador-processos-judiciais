# Imagem base
FROM python:3.11-slim

# Impedir buffering de logs (Boa prática da API)
ENV PYTHONUNBUFFERED=1

# Diretório de trabalho dentro do container
WORKDIR /app/ui

# Instalar dependências do sistema
# build-essential é necessário para compilar certas bibliotecas Python
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências. 
COPY ui/requirements-ui.txt ./requirements.txt

# Instalar dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código
COPY ui/. .

# Porta padrão do Streamlit
ENV PORT=8501

# Comando para rodar a interface Streamlit (CMD corrigido com -c)
CMD ["sh", "-c", "streamlit run app_interface.py --server.port=$PORT --server.address=0.0.0.0"]