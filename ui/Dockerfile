# ui/Dockerfile

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copia apenas as dependências da UI
COPY requirements-ui.txt .

RUN pip install --no-cache-dir -r requirements-ui.txt

# Copia TODO o código da UI
COPY . .

# Porta padrão do Streamlit
ENV PORT=8501
EXPOSE 8501

# Aqui o arquivo está direto em /app/app_interface.py
CMD ["streamlit", "run", "app_interface.py", "--server.port=8501", "--server.address=0.0.0.0"]
