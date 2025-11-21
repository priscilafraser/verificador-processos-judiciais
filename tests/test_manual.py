import json
from api.schemas.process_schema import Processo
from verifier.opniaoTecnica import gerar_parecer_tecnico

# Carregar JSON de exemplo
with open("tests/jsons/processo1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Validar com Pydantic
processo = Processo(**data)

# Gerar parecer técnico
parecer = gerar_parecer_tecnico(processo)

print("\n===== PARECER TÉCNICO =====")
print(parecer.model_dump())
