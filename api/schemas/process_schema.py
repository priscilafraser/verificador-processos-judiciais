from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class Documento(BaseModel):
    id: str
    dataHoraJuntada: datetime
    nome: str
    texto: str


class Movimento(BaseModel):
    dataHora: datetime
    descricao: str


class Processo(BaseModel):
    numeroProcesso: str
    classe: str
    orgaoJulgador: str
    ultimaDistribuicao: datetime
    assunto: str
    segredoJustica: bool
    justicaGratuita: bool
    siglaTribunal: str
    esfera: str
    
    valorCondenacao: Optional[float] = None

    documentos: List[Documento]
    movimentos: List[Movimento]

class ResultadoDecisao(BaseModel):
    decisao: str
    justificativa: str     
    citacoes: List[str]

