from fastapi.testclient import TestClient
import pytest

from api.app import app
from api.schemas.process_schema import Processo, Documento, Movimento, ResultadoDecisao


@pytest.fixture
def api_client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def payload_processo():
    doc = {
        "id": "1",
        "dataHoraJuntada": "2024-01-01T12:00:00",
        "nome": "Certidão de Trânsito em Julgado",
        "texto": "Trânsito em julgado certificado."
    }
    mov = {
        "dataHora": "2024-02-01T10:00:00",
        "descricao": "Cumprimento definitivo de sentença"
    }
    return {
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
        "documentos": [doc],
        "movimentos": [mov],
    }


def test_health_ok(api_client: TestClient):
    resp = api_client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "juscash-ml-api"


def test_analisar_processo_sucesso(api_client: TestClient, payload_processo, monkeypatch):
    def falsa_analise_com_llm(parecer):
        return ResultadoDecisao(
            decisao="approved",
            justificativa="Processo elegível.",
            citacoes=["POL-1", "POL-2"],
        )

    # PATCH NO ALVO CORRETO 
    monkeypatch.setattr("api.app.analisar_com_llm", falsa_analise_com_llm)

    resp = api_client.post("/analisar-processo", json=payload_processo)

    assert resp.status_code == 200
    body = resp.json()
    assert body["decisao"] == "approved"
    assert "POL-1" in body["citacoes"]
