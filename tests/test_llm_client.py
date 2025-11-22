import pytest

from api.schemas.process_schema import ResultadoDecisao
from verifier.opniaoTecnica import gerar_parecer_tecnico
from verifier.llm_client import analisar_com_llm, ErroLLM
from api.schemas.process_schema import Processo, Documento, Movimento
import verifier.llm_client as llm_module


def criar_processo_basico(
    esfera: str = "cível",
    valor_condenacao: float | None = 25000.0,
    com_transito: bool = True,
    em_execucao: bool = True,
) -> Processo:
    documentos = []
    movimentos = []

    if com_transito:
        documentos.append(
            Documento(
                id="1",
                dataHoraJuntada="2024-01-01T12:00:00",
                nome="Certidão de Trânsito em Julgado",
                texto="Trânsito em julgado certificado."
            )
        )

    if em_execucao:
        movimentos.append(
            Movimento(
                dataHora="2024-02-01T10:00:00",
                descricao="Início do cumprimento definitivo de sentença"
            )
        )

    return Processo(
        numeroProcesso="0000000-00.0000.0.00.0000",
        classe="Ação de Cobrança",
        orgaoJulgador="1ª Vara Federal",
        ultimaDistribuicao="2020-01-15T00:00:00",
        assunto="Cobrança",
        segredoJustica=False,
        justicaGratuita=True,
        siglaTribunal="TRF1",
        esfera=esfera,
        valorCondenacao=valor_condenacao,
        documentos=documentos,
        movimentos=movimentos,
    )


def test_analisar_com_llm_sucesso(monkeypatch):
    """
    Testa o fluxo do LLM simulando uma resposta válida.
    """

    def falsa_chamada_llm(prompt: str) -> str:
        # Simula o JSON que o modelo deveria retornar
        return """
        {
            "decisao": "approved",
            "justificativa": "Requisitos atendidos.",
            "citacoes": ["POL-1", "POL-2"]
        }
        """

    # Importamos a função interna que o analisar_com_llm usa
    monkeypatch.setattr(llm_module, "chamar_llm", falsa_chamada_llm)

    processo = criar_processo_basico()
    parecer = gerar_parecer_tecnico(processo)

    decisao = analisar_com_llm(parecer)

    assert isinstance(decisao, ResultadoDecisao)
    assert decisao.decisao == "approved"
    assert "POL-1" in decisao.citacoes

def test_analisar_com_llm_resposta_invalida(monkeypatch):
    """
    Testa o comportamento quando o LLM retorna algo que não é JSON válido.
    """

    def falsa_chamada_llm_invalido(prompt: str) -> str:
        return "isso não é JSON"

    import verifier.llm_client as llm_module
    monkeypatch.setattr(llm_module, "chamar_llm", falsa_chamada_llm_invalido)

    processo = criar_processo_basico()
    parecer = gerar_parecer_tecnico(processo)

    with pytest.raises(ErroLLM):
        analisar_com_llm(parecer)


