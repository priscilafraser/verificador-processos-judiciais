# tests/test_api_integration.py
import pytest
from fastapi.testclient import TestClient

from api.app import app
from api.schemas.process_schema import ResultadoDecisao


@pytest.mark.integration
def test_fluxo_completo_api_sem_llm_real(monkeypatch):
    """
    Teste de integração:
    - Envia payload para o endpoint
    - Passa por Pydantic, parecer técnico, etc.
    - Apenas a chamada LLM é mockada em nível baixo.
    """
    client = TestClient(app)

    from verifier import llm_client

    def fake_call_llm_raw(prompt: str) -> str:
        # Simulando o modelo retornando JSON válido
        return """
        {
            "decisao": "approved",
            "justificativa": "Todos os requisitos foram atendidos.",
            "citacoes": ["POL-1", "POL-2"]
        }
        """

    monkeypatch.setattr(llm_client, "chamar_llm", fake_call_llm_raw)

    payload = {
        "numeroProcesso": "0001111-11.2020.4.01.0000",
        "classe": "Ação de Cobrança",
        "orgaoJulgador": "1ª Vara Federal",
        "ultimaDistribuicao": "2020-01-15T00:00:00",
        "assunto": "Cobrança",
        "segredoJustica": False,
        "justicaGratuita": True,
        "siglaTribunal": "TRF1",
        "esfera": "cível",
        "valorCondenacao": 25000.0,
        "documentos": [
            {
                "id": "1",
                "dataHoraJuntada": "2024-01-01T12:00:00",
                "nome": "Certidão de Trânsito em Julgado",
                "texto": "..."
            }
        ],
        "movimentos": [
            {
                "dataHora": "2024-02-01T10:00:00",
                "descricao": "Cumprimento definitivo de sentença"
            }
        ],
    }

    resp = client.post("/analisar-processo", json=payload)
    assert resp.status_code == 200

    body = resp.json()
    assert body["decisao"] == "approved"
    assert "POL-1" in body["citacoes"]
