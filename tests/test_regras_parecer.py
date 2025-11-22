from api.schemas.process_schema import Processo, Documento, Movimento
from verifier.opniaoTecnica import gerar_parecer_tecnico


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


def test_parecer_completo_elegivel():
    processo = criar_processo_basico()
    parecer = gerar_parecer_tecnico(processo)

    assert parecer.numero_processo == processo.numeroProcesso
    assert not parecer.politicas_potencialmente_violadas
    assert "POL-1" in parecer.politicas_atendidas
    assert "POL-2" in parecer.politicas_atendidas
    assert parecer.analise.transitado_em_julgado is True
    assert parecer.analise.em_fase_execucao is True


def test_parecer_valor_abaixo():
    processo = criar_processo_basico(valor_condenacao=500.0)
    parecer = gerar_parecer_tecnico(processo)

    assert parecer.analise.valor_muito_baixo is True
    assert "POL-3" in parecer.politicas_potencialmente_violadas


def test_parecer_trabalhista():
    processo = criar_processo_basico(esfera="trabalhista")
    parecer = gerar_parecer_tecnico(processo)

    assert parecer.analise.esfera_trabalhista is True
    assert "POL-4" in parecer.politicas_potencialmente_violadas


def test_parecer_documentacao_incompleta():
    processo = criar_processo_basico(com_transito=False, em_execucao=False)
    parecer = gerar_parecer_tecnico(processo)

    assert parecer.analise.falta_documento_essencial is True
    assert "POL-8" in parecer.politicas_potencialmente_violadas
    assert any("trânsito" in d.lower() for d in parecer.analise.documentos_essenciais_faltantes)
