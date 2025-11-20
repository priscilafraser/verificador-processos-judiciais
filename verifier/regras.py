from pydantic import BaseModel
from typing import List, Optional

from api.schemas.process_schema import Processo

class ParecerTecnico(BaseModel):
    # politicas 1 e 2
    transitado_em_julgado: bool
    em_fase_execucao: bool
    valor_condenacao: Optional[float]

    # politicas 2 a 6
    valor_muito_baixo: bool          
    esfera_trabalhista: bool         
    obito_autor_sem_habilitacao: bool
    substabelecimento_sem_reserva: bool  

    # politica 7
    possui_informacao_honorarios: bool

    # politica 8
    falta_documento_essencial: bool 
    documentos_essenciais_faltantes: List[str]

    # Campo para comentarios
    observacoes: Optional[str] = None


def analisar_processo(processo: Processo) -> ParecerTecnico:
    # POL-1: transitado em julgado e em fase de execução
    transitado = temDocComNome(processo, "Trânsito em Julgado")
    # podemos considerar também variações:
    transitado = transitado or temDocComNome(processo, "Certidão de Trânsito")

    em_execucao = (
        temMovimentoComDescricao(processo, "cumprimento definitivo")
        or temMovimentoComDescricao(processo, "execução definitiva")
        or temMovimentoComDescricao(processo, "cumprimento de sentença")
    )

    # POL-2 / POL-3: valor de condenação + valor baixo
    valor_condenacao = processo.valorCondenacao
    valor_muito_baixo = (
        valor_condenacao is not None and valor_condenacao < 1000
    )

    # POL-4: esfera trabalhista
    esfera_trabalhista = processo.esfera.lower() == "trabalhista"

    # POL-5 e POL-6:
    # No schema base eles não vêm estruturados, então por enquanto
    # consideramos False e deixamos para o LLM tentar inferir pelo texto
    obito_autor_sem_habilitacao = False
    substabelecimento_sem_reserva = False

    # POL-7: honorários informados?
    # No schema base também não temos "honorarios", então marcamos False.
    possui_informacao_honorarios = False

    # POL-8: documento essencial faltante
    documentos_essenciais_faltantes = []

    if not transitado:
        documentos_essenciais_faltantes.append("Certidão de trânsito em julgado")

    if not em_execucao:
        documentos_essenciais_faltantes.append("Comprovação de fase de execução")

    falta_documento_essencial = len(documentos_essenciais_faltantes) > 0

    observacoes = None
    if falta_documento_essencial:
        observacoes = (
            "Foram identificadas ausências de documentos considerados essenciais "
            "para a análise completa da elegibilidade."
        )

    return ParecerTecnico(
        transitado_em_julgado=transitado,
        em_fase_execucao=em_execucao,
        valor_condenacao=valor_condenacao,
        valor_muito_baixo=valor_muito_baixo,
        esfera_trabalhista=esfera_trabalhista,
        obito_autor_sem_habilitacao=obito_autor_sem_habilitacao,
        substabelecimento_sem_reserva=substabelecimento_sem_reserva,
        possui_informacao_honorarios=possui_informacao_honorarios,
        falta_documento_essencial=falta_documento_essencial,
        documentos_essenciais_faltantes=documentos_essenciais_faltantes,
        observacoes=observacoes,
    )



def temDocComNome(processo: Processo, termo: str) -> bool:
    termoInferior = termo.lower()
    return any(termoInferior in doc.nome.lower() for doc in processo.documentos)



def temMovimentoComDescricao(processo: Processo, termo: str) -> bool:
    termoInferior = termo.lower()
    return any(termoInferior in mov.descricao.lower() for mov in processo.movimentos)
