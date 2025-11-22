from fastapi import FastAPI, HTTPException

from api.schemas.process_schema import Processo
from verifier.opniaoTecnica import gerar_parecer_tecnico
from verifier.llm_client import analisar_com_llm, ErroLLM
from config.logger import obter_log
import uuid
import time


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

    inicio_tempo_total = time.perf_counter()

    # Gera parecer técnico + chama llm
    try:
        tempo_inicio_parecer = time.perf_counter()
        parecer = gerar_parecer_tecnico(processo)
        parecer_tempo = time.perf_counter() - tempo_inicio_parecer
        logger.info(
            f"[{request_id}] Parecer gerado | numero_processo={processo.numeroProcesso} | "
            f"politicas_violadas={parecer.politicas_potencialmente_violadas}"
        )

        tempo_inicio_llm = time.perf_counter()
        decisao = analisar_com_llm(parecer)
        llm_tempo = time.perf_counter() - tempo_inicio_llm
        logger.info(
            f"[{request_id}] Decisão LLM | numero_processo={processo.numeroProcesso} | "
            f"decision={decisao.decisao} | citations={decisao.citacoes}"
        )

    except ErroLLM as e:
        tempo_total_llm_erro = time.perf_counter() - inicio_tempo_total
        logger.error(
            f"[{request_id}] Erro na decisão do LLM | numero_processo={processo.numeroProcesso} | "
            f"erro={e} | total_time={tempo_total_llm_erro:.3f}s"
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Falha ao obter decisão do LLM.",
                "details": str(e),
            },
        )

    except Exception as e:
        tempo_total_erros = time.perf_counter() - inicio_tempo_total
        logger.exception(
            f"[{request_id}] Erro inesperado ao analisar processo "
            f"| numero_processo={processo.numeroProcesso} | total_time={tempo_total_erros:.3f}s"
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Erro interno ao analisar o processo.",
                "details": str(e),
            },
        )
    

    # Resultado final
    tempo_total = time.perf_counter() - inicio_tempo_total
    logger.info(
        f"[{request_id}] Tempos | parecer={parecer_tempo:.3f}s | llm={llm_tempo:.3f}s | "
        f"total={tempo_total:.3f}s"
    )
    return decisao.model_dump()

