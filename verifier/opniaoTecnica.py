from pydantic import BaseModel
from typing import List

from api.schemas.process_schema import Processo
from verifier.regras import ParecerTecnico, analisar_processo


# Analise tecnica a partiri de um processo com base nas politicas
class OpniaoTecnica(BaseModel):

    numero_processo: str
    analise: ParecerTecnico   
    politicas_potencialmente_violadas: List[str]
    politicas_atendidas: List[str]
    resumo_tecnico: str      


def _mapear_politicas(analise: ParecerTecnico) -> tuple[list[str], list[str]]:
    violadas: list[str] = []
    atendidas: list[str] = []

    # POL-1: Só compramos crédito de processos transitados em julgado e em fase de execução.
    if analise.transitado_em_julgado and analise.em_fase_execucao:
        atendidas.append("POL-1")
    else:
        violadas.append("POL-1")

    # POL-2: Exigir valor de condenação informado.
    if analise.valor_condenacao is not None:
        atendidas.append("POL-2")
    else:
        violadas.append("POL-2")

    # POL-3: Valor de condenação < R$ 1.000,00 → não compra.
    if analise.valor_condenacao is not None and analise.valor_condenacao < 1000:
        violadas.append("POL-3")

    # POL-4: Condenações na esfera trabalhista → não compra.
    if analise.esfera_trabalhista:
        violadas.append("POL-4")

    # POL-5: Óbito do autor sem habilitação no inventário → não compra.
    if analise.obito_autor_sem_habilitacao:
        violadas.append("POL-5")

    # POL-6: Substabelecimento sem reserva de poderes → não compra.
    if analise.substabelecimento_sem_reserva:
        violadas.append("POL-6")

    # POL-7: Informar honorários contratuais, periciais e sucumbenciais quando existirem.
    # Aqui, como não temos os campos, só marcamos como atendida se o flag estiver True.
    if analise.possui_informacao_honorarios:
        atendidas.append("POL-7")

    # POL-8: Se faltar documento essencial → incomplete.
    if analise.falta_documento_essencial:
        violadas.append("POL-8")
    else:
        atendidas.append("POL-8")

    # Remover duplicados por segurança
    violadas = list(dict.fromkeys(violadas))
    atendidas = list(dict.fromkeys(atendidas))

    return violadas, atendidas


def _gerar_resumo_tecnico(
    numero_processo: str,
    analise: ParecerTecnico,
    politicas_violadas: list[str],
    politicas_atendidas: list[str],
) -> str:
    partes: list[str] = []

    partes.append(f"Processo {numero_processo}.")

    partes.append(
        f"Trânsito em julgado identificado: {'sim' if analise.transitado_em_julgado else 'não'}."
    )
    partes.append(
        f"Fase de execução confirmada: {'sim' if analise.em_fase_execucao else 'não'}."
    )

    if analise.valor_condenacao is not None:
        partes.append(f"Valor da condenação informado: R$ {analise.valor_condenacao:.2f}.")
        if analise.valor_muito_baixo:
            partes.append("O valor da condenação é inferior a R$ 1.000,00 (POL-3).")
    else:
        partes.append("Valor da condenação não foi informado.")

    if analise.esfera_trabalhista:
        partes.append("O processo está na esfera trabalhista (possível incidência da POL-4).")

    if analise.falta_documento_essencial:
        faltantes = ", ".join(analise.documentos_essenciais_faltantes) or "não especificados"
        partes.append(
            f"Foram identificadas ausências de documentos essenciais: {faltantes} (POL-8)."
        )

    if politicas_violadas:
        partes.append(
            "Com base na análise automática, há possíveis violações às seguintes políticas: "
            + ", ".join(politicas_violadas)
            + "."
        )

    if politicas_atendidas:
        partes.append(
            "As seguintes políticas parecem estar atendidas: "
            + ", ".join(politicas_atendidas)
            + "."
        )

    if analise.observacoes:
        partes.append(f"Observações adicionais: {analise.observacoes}")

    return " ".join(partes)


# Gera parecer estruturado para ser usado depois no prompt da LLM
def gerar_parecer_tecnico(process: Processo) -> OpniaoTecnica:

    # 1) Aplica as regras de negócio
    analise = analisar_processo(process)

    # 2) Mapeia as políticas relacionadas
    politicas_violadas, politicas_atendidas = _mapear_politicas(analise)

    # 3) Monta o resumo técnico em texto livre
    resumo = _gerar_resumo_tecnico(
        numero_processo=process.numeroProcesso,
        analise=analise,
        politicas_violadas=politicas_violadas,
        politicas_atendidas=politicas_atendidas,
    )

    # 4) Retorna o parecer completo
    return OpniaoTecnica(
        numero_processo=process.numeroProcesso,
        analise=analise,
        politicas_potencialmente_violadas=politicas_violadas,
        politicas_atendidas=politicas_atendidas,
        resumo_tecnico=resumo,
    )
