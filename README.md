# ⚖️ Análise Automatizada de Processos Judiciais com LLM + Regras de Negócio + FastAPI + Streamlit

## Visão Geral

O JusCash ML é um sistema inteligente para análise automatizada de processos judiciais, combinando:

- Regras determinísticas (POL-1 a POL-8)

- Módulo de Parecer Técnico

- LLM (OpenAI) para decisão final

- API FastAPI

- UI com Streamlit

- Observabilidade com logs estruturados, versionamento de prompts e métricas de latência

- Deploy em container (Docker) + link público

- Testes unitários e de integração (pytest)

O sistema recebe um processo judicial em JSON, aplica as políticas internas do case, gera um parecer técnico, chama o LLM com um prompt versionado e retorna uma decisão estruturada, justificativa e citações das políticas aplicadas.

## Funcionalidades

O sistema realiza uma análise automatizada de processos judiciais, combinando validações estruturais, interpretação de documentos e decisão assistida por IA. Entre as principais capacidades:

#### 1. API Backend (FastAPI + OpenAI)

- Recebe um processo no formato JSON e executa verificações sobre documentos, movimentações e consistência geral do caso.

- Identifica pontos críticos, possíveis inconsistências e informações faltantes.

- Consolida um parecer técnico estruturado, contendo itens encontrados, lacunas e observações relevantes.

- Repassa esse parecer para um modelo de IA (OpenAI), que produz uma decisão final padronizada, contendo:

  - Status (ex.: aprovado, rejeitado, incompleto)

  - Justificativa

  - Elementos citados no raciocínio

#### 2. Interface Web (Streamlit)

- Permite colar o JSON do processo.

- Botão Analisar processo que dispara a chamada da API.

- Exibe claramente a decisão (com cores indicativas).

- Mostra justificativa, elementos relevantes e citações da IA.

- Possui modo debug opcional para visualizar o JSON completo retornado pela API.


## Motor de Análise

O módulo de análise realiza:

- Extração de dados-chave do processo

- Avaliação da presença/ausência de documentos essenciais

- Interpretação de movimentações relevantes

- Identificação de eventuais inconsistências

- Consolidação dos achados em um parecer técnico rico e estruturado

## Camada de Decisão com IA
A engine interna envia o parecer técnico para um modelo de linguagem (OpenAI), que retorna:
````json
{
  "decision": "approved | rejected | incomplete",
  "rationale": "...",
  "citations": []
}
````

## Versionamento de Prompts
O comportamento da IA é controlado por arquivos de prompt versionados em:
````bash
verifier/prompts/prompt_v1.txt
verifier/prompts/prompt_v2.txt
````

A versão ativa é definida via variável de ambiente:
````ini
PROMPT_VERSION=1
````

Esse mecanismo permite ajustes de comportamento sem alterar código.

## Observabilidade

- Logs estruturados e padronizados

- IDs únicos por requisição

- Tempo total da análise e tempo isolado da IA

- Registro de falhas e exceções

- Métricas prontas para instrumentação externa

Nada sensível é logado — apenas indicadores operacionais.

## API Pública

GET /health — status geral do serviço

POST /analisar-processo — rota principal de análise

Entrada e saída em JSON documentado

Deploy conteinerizado, exposto em ambiente cloud

## Interface Web (Frontend)

A UI em Streamlit permite:

- Entrada de JSON

- Execução da análise

- Visualização da decisão

- Explicação textual

- Modo detalhado para depuração

Totalmente integrada com a API em produção.7

## Deploy e Infraestrutura

- Backend e frontend conteinerizados (Docker)

- Hospedados no Railway (back) e Streamlit Cloud (front)

- Variáveis de ambiente para segregar chaves e versões

- URLs públicas para avaliação e apresentação


## Estrutura do Projeto
````bash
juscash-ml
juscash-ml
│
├── api/
│   ├── app.py
│   └── schemas/
│       └── process_schema.py
│
├── config/
│   ├── __init__.py
│   └── logger.py
│
├── verifier/
│   ├── __init__.py
│   ├── regras.py
│   ├── opniaoTecnica.py
│   ├── llm_client.py
│   └── prompts/
│       ├── prompt_v1.txt
│       └── prompt_v2.txt
│        ..
│
├── ui/
│   ├── __init__.py
│   ├── app_interface.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── tests/
│   ├── __pycache__/
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_api_integracao.py
│   ├── test_llm_client.py
│   ├── test_regras_parecer.py
│   ├── test_schemas.py
│   ├── testes_iniciais/
│   │   ├── teste_integrado.py
│   │   └── teste_manual.py
│   └── jsons/
│       └── processo1.json
│
├── .dockerignore
├── .env                  # NÃO vai para produção
├── .gitignore
├── Dockerfile            # Dockerfile da API
├── LICENSE
├── pytest.ini
├── README.md
├── requirements.txt      # requirements da API
└── run.py    
````

## Testes
A cobertura de testes foi estruturada em três camadas principais:

✔ Testes Unitários

- Validação das regras de negócio do parecer técnico

- Testes dos modelos Pydantic (validação de input/output)

- Verificação da lógica de montagem do parecer

✔ Testes do Módulo de IA (mockados)

- Simulação de resposta válida

- Simulação de erros na chamada à IA

- Validação da conversão para o objeto de decisão final

✔ Testes de Integração

- Chamada real ao endpoint /analisar-processo

- Mock parcial apenas no LLM

- Verificação do JSON final retornado

Para executar:
````bash
pytest
````

## Containerização (Docker)
O projeto possui dois serviços independentes: API (FastAPI) e Interface Web (Streamlit).
Cada um possui sua própria imagem Docker.

### API (FastAPI)

Build
````bash
docker build -t juscash-ml-api .
````

Executar local
````bash
docker run --rm -p 8000:8000 \
  -e OPENAI_API_KEY="sua_key" \
  -e PROMPT_VERSION=1 \
  juscash-ml-api
````

API disponível em:
````bash
http://localhost:8000
````

### Interface (UI – Streamlit)

Build
````bash
docker build -f ui/Dockerfile -t juscash-ui ui
````

Executar local
````bash
docker run --rm -p 8501:8501 \
  -e JUSCASH_API_URL="https://verificador-processos-judiciais-production.up.railway.app" \
  juscash-ui
````

API disponível em:
````bash
http://localhost:8501
````

## Deploy em produção

### API – JusCash ML (Railway)

A API foi publicada na plataforma Railway, utilizando o Dockerfile presente na raiz do projeto.

- Plataforma: Railway

- Build: Dockerfile (juscash-ml-api)

Variáveis de ambiente utilizadas:

  - OPENAI_API_KEY – chave da OpenAI usada pelo modelo

  - PROMPT_VERSION – versão do prompt carregado pelo serviço (ex.: 1)

URL pública da API:
````bash
https://verificador-processos-judiciais-production.up.railway.app/
````

### Interface Web (Streamlit)

A interface Streamlit foi publicada em um serviço separado, também na plataforma Railway, usando imagem Docker própria.

- Plataforma: Streamlit Community Cloud

- Build/Deploy: Deploy direto do repositório GitHub

Variáveis de ambiente utilizadas:

  - JUSCASH_API_URL – URL base da API em produção, consumida pela UI
(ex.: https://juscash-ml-api.up.railway.app)

Acesse a aplicação no link abaixo:
````bash
https://verificador-proceapps-judiciais.streamlit.app/
````


## Rotas da API

GET /health

Rota simples para verificação de disponibilidade do serviço.

Exemplo de resposta:
````json
{
  "status": "ok",
  "service": "juscash-ml-api"
}
````

POST /analisar-processo

Recebe o JSON de um processo judicial e retorna uma análise estruturada contendo:

- decisão (ex.: aprovado, rejeitado, incompleto)

- justificativa textual

- referências/pontos avaliados pelo modelo

Exemplo de resposta:
````json
{
  "decision": "approved",
  "rationale": "Processo atende aos requisitos...",
  "citations": ["POL-1", "POL-2"]
}
````

#### Variáveis de Ambiente
````ini
OPENAI_API_KEY=...
PROMPT_VERSION=1
````

## Pontos Fortes Técnicos
- Estrutura organizada e fácil de entender

- Versionamento de prompts (controle de evolução do modelo)

- Validações fortes com Pydantic

- Logs e observabilidade incorporados desde o início

- Conjunto de testes cobrindo regras, API e integração

- Backend em FastAPI + UI em Streamlit

- Deploy completo via containers (API + Interface)


## Licença

Livre para uso educacional ou análise de código.


### 🧑‍💻 Autor

Projeto desenvolvido para estudo e demonstração de estratégias de detecção de ameaças com Machine Learning e análise inteligente de logs, aplicando técnicas de Detecção de Anomalias e práticas de Segurança Cibernética (Blue Team).
| [<img src="https://avatars.githubusercontent.com/u/55546267?v=4" width=115><br><sub>Priscila Miranda</sub>](https://github.com/priscilafraser) |
| :---: |
