"""Schemas da API do EduMap."""
from pydantic import BaseModel, Field
from typing import List


class Notas(BaseModel):
    linguagens: float = Field(..., ge=0, le=1000)
    humanas: float = Field(..., ge=0, le=1000)
    natureza: float = Field(..., ge=0, le=1000)
    matematica: float = Field(..., ge=0, le=1000)
    redacao: float = Field(..., ge=0, le=1000)


class PredictRequest(BaseModel):
    interesse: str
    grau: str
    modalidade: str
    notas: Notas


class CursoRecomendado(BaseModel):
    nome: str
    chance: float


class PredictResponse(BaseModel):
    perfil: str
    cluster: int
    cursos: List[CursoRecomendado]