import pytest
from pydantic import ValidationError
from datetime import datetime

from api.schemas.process_schema import Processo, Documento, Movimento, ResultadoDecisao

def test_documento_valido():
    doc = Documento(
        id="1",
        dataHoraJuntada="2024-01-01T12:00:00",
        nome="Petiçao inicial",
        texto="Texto qualquer"
    )
    assert doc.id == "1"
    assert doc.nome == "Petiçao inicial"

def test_movimento_valido():
    mov = Movimento(
        dataHora="2024-01-02T10:00:00",
        descricao="Sentença de procedência"
    )
    assert "Sentença" in mov.descricao


def test_processo_valido():
    processo = Processo(
        numeroProcesso="000123",
        classe="Ação Cível",
        orgaoJulgador="1ª Vara Cível",
        ultimaDistribuicao=datetime(2024, 1, 1, 10, 0, 0),
        assunto="Cobrança",
        segredoJustica=False,
        justicaGratuita=True,
        siglaTribunal="TJXX",
        esfera="Estadual",
        valorCondenacao=25000.0,
        documentos=[
            Documento(
                id="1",
                dataHoraJuntada=datetime(2024, 1, 1, 0, 0, 0),
                nome="Petição Inicial",
                texto="Conteúdo da petição"
            )
        ],
        movimentos=[
            Movimento(
                dataHora=datetime(2024, 1, 2, 15, 30, 0),
                descricao="Distribuição do processo"
            )
        ]
    )

    assert processo.numeroProcesso.startswith("000")
    assert processo.valorCondenacao == 25000.0
    assert len(processo.documentos) == 1
    assert len(processo.movimentos) == 1


def test_processo_invalido_falta_campo_obrigatorio():
    with pytest.raises(ValidationError):
        Processo(
            numeroProcesso="123",
            # classe faltando, entre outros campos obrigatórios
            orgaoJulgador="1ª Vara",
            ultimaDistribuicao="2024-01-01T00:00:00",
            assunto="Teste",
            segredoJustica=False,
            justicaGratuita=False,
            siglaTribunal="TRF1",
            esfera="cível",
            documentos=[],
            movimentos=[],
        )


def test_resultado_decisao_valido():
    resultado = ResultadoDecisao(
        decisao="approved",
        justificativa="Tudo ok.",
        citacoes=["POL-1", "POL-2"],
    )
    assert resultado.decisao == "approved"
    assert "POL-1" in resultado.citacoes


