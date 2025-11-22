import json
from api.schemas.process_schema import Processo
from verifier.opniaoTecnica import gerar_parecer_tecnico
from verifier.llm_client import analisar_com_llm

with open("tests/jsons/processo1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

processo = Processo(**data)
parecer = gerar_parecer_tecnico(processo)
decisao = analisar_com_llm(parecer)

print(decisao.model_dump())
