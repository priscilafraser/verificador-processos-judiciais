import json
import os
from typing import Any
from openai import OpenAI
from pydantic import ValidationError

from api.schemas.process_schema import ResultadoDecisao
from verifier.opniaoTecnica import OpniaoTecnica
from dotenv import load_dotenv
from config.logger import obter_log


load_dotenv()

logger = obter_log("llm")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Carregando template
def carregarPrompt(path: str = None) -> str:

    versao = os.getenv("PROMPT_VERSION", "1")
    logger.info(f"Usando prompt versão {versao}")

    if path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "prompts", f"prompt_v{versao}.txt")

    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    

# Constroi o prompt final, injetando o JSON do parecer técnico
def construirPrompt(opniao_tecnica: OpniaoTecnica) -> str:

    template = carregarPrompt()
    opiniao_json = opniao_tecnica.model_dump_json(ensure_ascii=False)

    prompt = template.replace("{technical_opinion_json}", opiniao_json)
    return prompt

class ErroLLM(Exception):
    # Tratamento de um possivel erro
    pass

# Faz a chamada bruta ao LLM
def chamar_llm(prompt: str, modelo: str = None) -> str:
    
    if modelo is None:
        modelo = os.getenv("JUSCASH_LLM_MODELO", "gpt-4.1-mini")

    resposta = client.chat.completions.create(
        model=modelo,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0.1,
    )

    conteudo = resposta.choices[0].message.content

    if conteudo is None:
        raise ErroLLM("Resposta vazia do LLM.")

    return conteudo.strip()


# Para extrair json de um texto
def _extrair_json(texto: str) -> Any:
    # Tentativa direta
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        pass

    # Tentativa: pegar o trecho entre o primeiro '{' e o último '}'
    inicio = texto.find("{")
    fim = texto.rfind("}")
    if inicio != -1 and fim != -1 and fim > inicio:
        try:
            return json.loads(texto[inicio : fim + 1])
        except json.JSONDecodeError:
            pass

    raise ErroLLM(f"Não foi possível interpretar a saída do LLM como JSON: {texto}")


# Função principal do módulo
def analisar_com_llm(opiniao_tecnica: OpniaoTecnica) -> ResultadoDecisao:

    logger.info(
        "Chamando LLM para decisão | numero_processo=%s | politicas_violadas=%s",
        opiniao_tecnica.numero_processo,
        opiniao_tecnica.politicas_potencialmente_violadas,
    )

    # Monta o prompt
    prompt = construirPrompt(opiniao_tecnica)

    # Chamar a llm
    res = chamar_llm(prompt)

    # Extrair json da resposta
    data = _extrair_json(res)

    # Validar com Pydantic
    try:
        decisao = ResultadoDecisao(**data)
    except ValidationError as e:
        logger.error("Resposta do LLM não bate com DecisionResult | erro=%s", e)
        raise ErroLLM(f"Resposta do LLM não atende ao schema ResultadoDecisao: {e}") from e

    logger.info(
        "Decisão validada | numero_processo=%s | decision=%s",
        opiniao_tecnica.numero_processo,
        decisao.decisao,
    )
    return decisao
