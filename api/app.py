from flask import Flask, jsonify, request
from pydantic import ValidationError
import json

from api.schemas.process_schema import Processo
from verifier.opniaoTecnica import gerar_parecer_tecnico
from verifier.llm_client import analisar_com_llm, ErroLLM

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():

    return jsonify(
        {
            "status": "ok",
            "service": "juscash-ml-api",
        }
    ), 200


# Endpoint principal
@app.route("/analisar-processo", methods=["POST"])
def analisar_processo():
    
    # Json de entrada
    try:
        requisicao = request.get_json(force=True)
    except Exception:
        return (
            jsonify({"error": "JSON inválido no corpo da requisição."}),
            400,
        )

    # Valida com pydantic
    try:
        processo = Processo(**requisicao)
    except ValidationError as e:
        return (
            jsonify(
                {
                    "error": "Payload não está no formato esperado para Processo.",
                    "details": json.loads(e.json()),
                }
            ),
            400,
        )

    # Gera parecer técnico + chama llm
    try:
        parecer = gerar_parecer_tecnico(processo)
        decisao = analisar_com_llm(parecer)
    except ErroLLM as e:
        return (
            jsonify(
                {
                    "error": "Falha ao obter decisão do LLM.",
                    "details": str(e),
                }
            ),
            500,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "error": "Erro interno ao analisar o processo.",
                    "details": str(e),
                }
            ),
            500,
        )

    # Resultado final
    return jsonify(decisao.model_dump()), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)