from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import json

from api.schemas.process_schema import Processo
from verifier.opniaoTecnica import gerar_parecer_tecnico
from verifier.llm_client import analisar_com_llm, ErroLLM
from config.logger import obter_log
import uuid


app = FastAPI(
    title="JusCash ML API",
    version="1.0.0",
    description="API para análise automatizada de processos judiciais."
)

logger = obter_log("api")

@app.get("/health")
def health():

    return {
            "status": "ok",
            "service": "juscash-ml-api",
        }


# Endpoint principal
@app.post("/analisar-processo")
def analisar_processo(processo: Processo):
    
    request_id = str(uuid.uuid4())
    logger.info(f"[{request_id}] Nova requisição /analisar-processo recebida")

    # Gera parecer técnico + chama llm
    try:
        parecer = gerar_parecer_tecnico(processo)
        logger.info(
            f"[{request_id}] Parecer gerado | numero_processo={processo.numeroProcesso} | "
            f"politicas_violadas={parecer.politicas_potencialmente_violadas}"
        )

        decisao = analisar_com_llm(parecer)
        logger.info(
            f"[{request_id}] Decisão LLM | numero_processo={processo.numeroProcesso} | "
            f"decision={decisao.decisao} | citations={decisao.citacoes}"
        )

    except ErroLLM as e:
        logger.error(
            f"[{request_id}] Erro na decisão do LLM | numero_processo={processo.numeroProcesso} | erro={e}"
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Falha ao obter decisão do LLM.",
                "details": str(e),
            },
        )

    except Exception as e:
        logger.exception(
            f"[{request_id}] Erro inesperado ao analisar processo "
            f"| numero_processo={processo.numeroProcesso}"
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Erro interno ao analisar o processo.",
                "details": str(e),
            },
        )
    

    # Resultado final
    return decisao.model_dump()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)