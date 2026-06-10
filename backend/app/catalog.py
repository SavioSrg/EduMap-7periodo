
"""Catálogo carregado a partir de `catalogo.pkl` e enriquecido com `categorias.json`.

O pickle contém os cursos base, com:
- `CODIGO_CURSO`
- `NOME_CURSO`
- `SIGLA_IES`

Este módulo:
1. carrega o pickle;
2. cruza o nome do curso com o arquivo `categorias.json`;
3. atribui uma área principal (`area`) e, quando possível, um grau (`grau`);
4. expõe a função `filtrar(area, grau)` usada pela API.
"""
from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib

_CATEGORIAS_PATH = "models/categorias.json"
_CATALOGO_PATH = "models/catalogo.pkl"

_NO_PREF = {
    "",
    "não tenho preferência",
    "nao tenho preferencia",
    "qualquer",
    "todos",
    "todas",
    "sem preferência",
    "sem preferencia",
    "nenhuma",
}

_AREA_ALIASES = {
    "DIREITO": "Direito e Ciências Sociais",
    "CIENCIAS SOCIAIS": "Direito e Ciências Sociais",
    "CIÊNCIAS SOCIAIS": "Direito e Ciências Sociais",
    "ARTES": "Artes e Design",
    "DESIGN": "Artes e Design",
    "EDUCACAO": "Educação",
    "EDUCAÇÃO": "Educação",
    "SAUDE": "Saúde",
    "SAÚDE": "Saúde",
    "TECNOLOGIA": "Tecnologia",
    "ENGENHARIAS": "Engenharias",
    "NEGOCIOS": "Negócios",
    "NEGÓCIOS": "Negócios",
    "AGRARIAS": "Agrárias",
    "AGRÁRIAS": "Agrárias",
}

_TECNOLOGICO = {
    "ANÁLISE E DESENVOLVIMENTO DE SISTEMAS",
    "ANALISE E DESENVOLVIMENTO DE SISTEMAS",
    "AUTOMAÇÃO INDUSTRIAL",
    "AUTOMACAO INDUSTRIAL",
    "GESTÃO AMBIENTAL",
    "GESTAO AMBIENTAL",
    "GESTÃO COMERCIAL",
    "GESTAO COMERCIAL",
    "GESTÃO DA TECNOLOGIA DA INFORMAÇÃO",
    "GESTAO DA TECNOLOGIA DA INFORMACAO",
    "GESTÃO DE RECURSOS HUMANOS",
    "GESTAO DE RECURSOS HUMANOS",
    "GESTÃO DE SERVIÇOS DE SAÚDE",
    "GESTAO DE SERVICOS DE SAUDE",
    "GESTÃO DE TURISMO",
    "GESTAO DE TURISMO",
    "GESTÃO EM SAÚDE",
    "GESTAO EM SAUDE",
    "GESTÃO PÚBLICA",
    "GESTAO PUBLICA",
    "MARKETING",
    "LOGÍSTICA",
    "LOGISTICA",
    "PROCESSOS GERENCIAIS",
    "REDES DE COMPUTADORES",
    "SISTEMAS PARA INTERNET",
    "ESTÉTICA E COSMÉTICA",
    "ESTETICA E COSMETICA",
    "AGRONEGÓCIO",
    "AGRONEGOCIO",
    "GESTÃO DE AGRONEGÓCIOS",
    "GESTAO DE AGRONEGOCIOS",
    "COMÉRCIO EXTERIOR",
    "COMERCIO EXTERIOR",
    "RADIOLOGIA",
}

_ABI = {
    "ABI - CIÊNCIAS BIOLÓGICAS",
    "ABI - CIENCIAS BIOLOGICAS",
    "ABI - CIÊNCIAS SOCIAIS",
    "ABI - CIENCIAS SOCIAIS",
    "ABI - EDUCAÇÃO FÍSICA",
    "ABI - EDUCACAO FISICA",
    "ABI - FILOSOFIA",
    "ABI - FÍSICA",
    "ABI - FISICA",
    "ABI - GEOGRAFIA",
    "ABI - HISTÓRIA",
    "ABI - HISTORIA",
    "ABI - LETRAS",
    "ABI - MATEMÁTICA",
    "ABI - MATEMATICA",
    "ABI - QUÍMICA",
    "ABI - QUIMICA",
}

_LICENCIATURA = {
    "BIOLOGIA",
    "EDUCAÇÃO FÍSICA",
    "EDUCACAO FISICA",
    "FÍSICA",
    "FISICA",
    "GEOGRAFIA",
    "HISTÓRIA",
    "HISTORIA",
    "LETRAS",
    "MATEMÁTICA",
    "MATEMATICA",
    "PEDAGOGIA",
    "QUÍMICA",
    "QUIMICA",
    "CIÊNCIAS BIOLÓGICAS",
    "CIENCIAS BIOLOGICAS",
    "FILOSOFIA",
}

_BACHARELADO = {
    "ADMINISTRAÇÃO",
    "ADMINISTRACAO",
    "CIÊNCIAS CONTÁBEIS",
    "CIENCIAS CONTABEIS",
    "CIÊNCIAS ECONÔMICAS",
    "CIENCIAS ECONOMICAS",
    "DIREITO",
    "MEDICINA",
    "ENFERMAGEM",
    "ODONTOLOGIA",
    "FISIOTERAPIA",
    "FARMÁCIA",
    "FARMACIA",
    "NUTRIÇÃO",
    "NUTRICAO",
    "PSICOLOGIA",
    "AGRONOMIA",
    "ZOOTECNIA",
    "ENGENHARIA CIVIL",
    "ENGENHARIA ELÉTRICA",
    "ENGENHARIA ELETRICA",
    "ENGENHARIA MECÂNICA",
    "ENGENHARIA MECANICA",
    "ENGENHARIA DE PRODUÇÃO",
    "ENGENHARIA QUÍMICA",
    "ENGENHARIA QUIMICA",
    "ENGENHARIA DE ALIMENTOS",
    "ENGENHARIA AMBIENTAL",
    "ENGENHARIA FLORESTAL",
    "ENGENHARIA DE BIOPROCESSOS",
    "ENGENHARIA DE AUTOMAÇÃO INDUSTRIAL",
    "ENGENHARIA DE AUTOMACAO INDUSTRIAL",
    "ENGENHARIA DE COMPUTAÇÃO",
    "ENGENHARIA DE COMPUTACAO",
    "ENGENHARIA DE SOFTWARE",
    "CIÊNCIA DA COMPUTAÇÃO",
    "CIENCIA DA COMPUTACAO",
    "CIÊNCIA DE DADOS",
    "CIENCIA DE DADOS",
    "SISTEMAS DE INFORMAÇÃO",
    "SISTEMAS DE INFORMACAO",
    "ARQUITETURA E URBANISMO",
    "ARQUIVOLOGIA",
    "ANTROPOLOGIA",
    "CIÊNCIAS SOCIAIS",
    "CIENCIAS SOCIAIS",
    "RELAÇÕES INTERNACIONAIS",
    "RELACOES INTERNACIONAIS",
    "SERVIÇO SOCIAL",
    "SERVICO SOCIAL",
    "ARTES VISUAIS",
    "MÚSICA",
    "MUSICA",
    "TEATRO",
    "DESIGN",
    "DESIGN DE AMBIENTES",
    "DESIGN DE INTERIORES",
    "DESIGN DE MODA",
    "DESIGN DE PRODUTO",
    "DESIGN GRÁFICO",
    "DESIGN GRAFICO",
}


def _normalizar(texto: str) -> str:
    texto = texto.strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = re.sub(r"\s+", " ", texto)
    return texto.upper()


@lru_cache(maxsize=1)
def _carregar_categorias() -> Dict[str, List[str]]:
    if _CATEGORIAS_PATH.exists():
        with _CATEGORIAS_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    # fallback em memória
    return {
        "Tecnologia": [
            "CIÊNCIA DA COMPUTAÇÃO",
            "ENGENHARIA DE COMPUTAÇÃO",
            "SISTEMAS DE INFORMAÇÃO",
            "ENGENHARIA DE SOFTWARE",
            "CIÊNCIA DE DADOS",
            "MATEMÁTICA COMPUTACIONAL",
            "REDES DE COMPUTADORES",
            "ANÁLISE E DESENVOLVIMENTO DE SISTEMAS",
        ],
        "Engenharias": [
            "ENGENHARIA CIVIL",
            "ENGENHARIA ELÉTRICA",
            "ENGENHARIA MECÂNICA",
            "ENGENHARIA DE PRODUÇÃO",
            "ENGENHARIA QUÍMICA",
            "ENGENHARIA DE ALIMENTOS",
            "ENGENHARIA AMBIENTAL",
            "ENGENHARIA DE AUTOMAÇÃO INDUSTRIAL",
            "ENGENHARIA DE BIOPROCESSOS",
        ],
        "Saúde": [
            "MEDICINA",
            "MEDICINA VETERINÁRIA",
            "ENFERMAGEM",
            "ODONTOLOGIA",
            "FISIOTERAPIA",
            "FARMÁCIA",
            "NUTRIÇÃO",
            "PSICOLOGIA",
            "EDUCAÇÃO FÍSICA",
        ],
        "Agrárias": [
            "AGRONOMIA",
            "ZOOTECNIA",
            "ENGENHARIA FLORESTAL",
            "MEDICINA VETERINÁRIA",
        ],
        "Educação": [
            "PEDAGOGIA",
            "MATEMÁTICA",
            "FÍSICA",
            "QUÍMICA",
            "BIOLOGIA",
            "HISTÓRIA",
            "GEOGRAFIA",
            "LETRAS",
        ],
        "Negócios": [
            "ADMINISTRAÇÃO",
            "CIÊNCIAS CONTÁBEIS",
            "CIÊNCIAS ECONÔMICAS",
            "CONTROLADORIA E FINANÇAS",
            "LOGÍSTICA",
            "MARKETING",
            "GESTÃO COMERCIAL",
        ],
        "Direito e Ciências Sociais": [
            "DIREITO",
            "CIÊNCIAS SOCIAIS",
            "RELAÇÕES INTERNACIONAIS",
            "SERVIÇO SOCIAL",
        ],
        "Artes e Design": [
            "DESIGN",
            "DESIGN DE AMBIENTES",
            "DESIGN DE INTERIORES",
            "DESIGN DE MODA",
            "ARTES VISUAIS",
            "MÚSICA",
            "TEATRO",
        ],
    }


def _carregar_catalogo_base() -> List[Dict[str, Any]]:
    if not _CATALOGO_PATH.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {_CATALOGO_PATH}. "
            "Coloque o catalogo.pkl no mesmo diretório de catalog.py."
        )
    dados = joblib.load(_CATALOGO_PATH)
    if not isinstance(dados, list):
        raise ValueError("O arquivo catalogo.pkl deve conter uma lista de dicionários.")
    return dados


@lru_cache(maxsize=1)
def _mapa_cursos_para_areas() -> Dict[str, List[str]]:
    categorias = _carregar_categorias()
    mapa: Dict[str, List[str]] = {}
    for area, cursos in categorias.items():
        for curso in cursos:
            chave = _normalizar(curso)
            mapa.setdefault(chave, [])
            if area not in mapa[chave]:
                mapa[chave].append(area)
    return mapa


def _areas_por_nome(nome_curso: str) -> List[str]:
    nome_norm = _normalizar(nome_curso)
    mapa = _mapa_cursos_para_areas()

    if nome_norm in mapa:
        return mapa[nome_norm]

    if nome_norm.startswith("ENGENHARIA"):
        return ["Engenharias"]

    if any(token in nome_norm for token in (
        "MEDICINA", "ENFERMAGEM", "ODONTOLOGIA", "FISIOTERAPIA", "FARMACIA",
        "NUTRICAO", "PSICOLOGIA", "BIOMEDICINA", "FONOAUDIOLOGIA", "ESTETICA",
        "COSMETICA",
    )):
        return ["Saúde"]

    if any(token in nome_norm for token in (
        "AGRONOMIA", "ZOOTECNIA", "AGRO", "AQUACULTURA", "AGRONEGOCIO",
        "VETERINARIA", "FLORESTAL",
    )):
        return ["Agrárias"]

    if any(token in nome_norm for token in (
        "DIREITO", "CIENCIAS SOCIAIS", "RELACOES INTERNACIONAIS",
        "SERVICO SOCIAL", "ANTROPOLOGIA", "SOCIOLOGIA",
    )):
        return ["Direito e Ciências Sociais"]

    if any(token in nome_norm for token in (
        "DESIGN", "ARTES", "MUSICA", "TEATRO", "CINEMA", "AUDIOVISUAL",
    )):
        return ["Artes e Design"]

    if any(token in nome_norm for token in (
        "ADMINISTRACAO", "CONTABEIS", "ECONOMICAS", "FINANCAS", "LOGISTICA",
        "MARKETING", "GESTAO", "TURISMO", "COMERCIO EXTERIOR", "ATUARIAIS",
        "RECURSOS HUMANOS",
    )):
        return ["Negócios"]

    if nome_norm.startswith("ABI -") or any(token in nome_norm for token in (
        "PEDAGOGIA", "LETRAS", "HISTORIA", "GEOGRAFIA", "MATEMATICA",
        "FISICA", "QUIMICA", "BIOLOGIA", "FILOSOFIA", "EDUCACAO FISICA",
        "CIENCIAS BIOLOGICAS",
    )):
        return ["Educação"]

    if any(token in nome_norm for token in (
        "COMPUTACAO", "INFORMATICA", "SISTEMAS", "DADOS", "REDES", "AUTOMACAO",
        "ESTATISTICA", "BIOTECNOLOGIA", "CIENCIA E TECNOLOGIA", "INOVACAO, CIENCIA E TECNOLOGIA",
        "CIENCIAS EXATAS", "CIENCIAS ATMOSFERICAS", "SISTEMA DE INFORMACAO",
    )):
        return ["Tecnologia"]

    if any(token in nome_norm for token in (
        "ALIMENTOS", "PROCESSOS QUIMICOS", "CIENCIA E TECNOLOGIA DE ALIMENTOS",
        "CIENCIA E TECNOLOGIA DE LATICINIOS", "PRODUCAO SUCROALCOOLEIRA",
        "GEOLOGIA",
    )):
        return ["Engenharias"]

    if any(token in nome_norm for token in (
        "ARQUITETURA E URBANISMO", "MODA", "JORNALISMO", "PUBLICIDADE E PROPAGANDA",
        "PRODUCAO PUBLICITARIA", "RELACOES PUBLICAS", "RADIO, TV E INTERNET",
        "COMUNICACAO SOCIAL", "CONSERVACAO E RESTAURO", "CONSERVACAO E RESTAURACAO",
        "ARTES CENICAS", "ARTES PLASTICAS",
    )):
        return ["Artes e Design"]

    if any(token in nome_norm for token in (
        "ARQUIVOLOGIA", "BIBLIOTECONOMIA", "CIENCIAS DA RELIGIAO", "CIENCIAS DO ESTADO",
        "CIENCIAS HUMANAS",
    )):
        return ["Direito e Ciências Sociais"]

    if any(token in nome_norm for token in (
        "TERAPIA OCUPACIONAL", "RADIOLOGIA",
    )):
        return ["Saúde"]

    if any(token in nome_norm for token in (
        "PROCESSOS GERENCIAIS", "CIENCIAS SOCIOAMBIENTAIS",
        "INTERDISCIPLINAR EM CIENCIA E ECONOMIA",
    )):
        return ["Negócios"]

    if "MUSEOLOGIA" in nome_norm:
        return ["Artes e Design"]

    return []


def _grau_por_curso(nome_curso: str, areas: List[str]) -> str:
    nome_norm = _normalizar(nome_curso)

    if nome_norm.startswith("ABI -"):
        return "Licenciatura" if "Educação" in areas else "Bacharelado"

    if "LICENCIATURA" in nome_norm:
        return "Licenciatura"

    if "Educação" in areas:
        return "Licenciatura"

    if nome_norm in _TECNOLOGICO:
        return "Tecnológico"

    if nome_norm in _LICENCIATURA:
        return "Licenciatura"

    if nome_norm in _BACHARELADO:
        return "Bacharelado"

    return "Bacharelado"


def _e_no_pref(valor: Optional[str]) -> bool:
    if valor is None:
        return True
    return _normalizar(valor) in {_normalizar(item) for item in _NO_PREF}


def _normalizar_area(area: Optional[str]) -> Optional[str]:
    if not area:
        return None
    area_norm = _normalizar(area)
    return _AREA_ALIASES.get(area_norm, area.strip())


@lru_cache(maxsize=1)
def carregar_catalogo() -> List[Dict[str, Any]]:
    dados = _carregar_catalogo_base()
    catalogo: List[Dict[str, Any]] = []

    for item in dados:
        nome = str(item.get("NOME_CURSO", "")).strip()
        codigo = item.get("CODIGO_CURSO")
        ies = str(item.get("SIGLA_IES", "")).strip()
        areas = _areas_por_nome(nome)
        area_principal = areas[0] if areas else "Outros"
        grau = str(item.get("GRAU", "")).strip()
            
        if not grau:
            grau = _grau_por_curso(nome, areas)

        catalogo.append(
            {
                "codigo_curso": codigo,
                "CODIGO_CURSO": codigo,
                "nome": nome,
                "NOME_CURSO": nome,
                "sigla_ies": ies,
                "SIGLA_IES": ies,
                "areas": areas,
                "area": area_principal,
                "grau": grau,
            }
        )

    return catalogo


CATALOG: List[Dict[str, Any]] = carregar_catalogo()

from collections import defaultdict


@lru_cache(maxsize=1)
def catalogo_por_area_grau():
    estrutura = defaultdict(
        lambda: defaultdict(list)
    )

    for curso in CATALOG:
        estrutura[
            curso["area"]
        ][
            curso["grau"]
        ].append(curso)

    return {
        area: dict(graus)
        for area, graus in estrutura.items()
    }


def filtrar(area: str, grau: str) -> List[Dict[str, Any]]:
    """Retorna cursos do catálogo filtrados por área e grau.

    - `area` vazio ou equivalente a "Não tenho preferência" devolve todos os cursos.
    - `grau` vazio ou equivalente a "Não tenho preferência" não filtra por grau.
    - quando a combinação área + grau não encontra nada, o fallback devolve
      primeiro apenas a área; se ainda assim não houver match, devolve o catálogo inteiro.
    """
    pool = CATALOG

    if not _e_no_pref(area):
        area_normalizada = _normalizar_area(area)
        pool = [
            c for c in pool
            if area_normalizada in c.get("areas", []) or c.get("area") == area_normalizada
        ]

    if not _e_no_pref(grau):
        grau_norm = _normalizar(grau)
        pool = [c for c in pool if _normalizar(c.get("grau", "")) == grau_norm]

    if not pool and not _e_no_pref(area):
        area_normalizada = _normalizar_area(area)
        pool = [
            c for c in CATALOG
            if area_normalizada in c.get("areas", []) or c.get("area") == area_normalizada
        ]

    if not pool:
        pool = CATALOG

    return pool

def filtrar_por_area_grau(
    area: Optional[str] = None,
    grau: Optional[str] = None,
):
    dados = catalogo_por_area_grau()

    if _e_no_pref(area):
        return dados

    area = _normalizar_area(area)

    if area not in dados:
        return {}

    if _e_no_pref(grau):
        return dados[area]

    return {
        grau: dados[area].get(grau, [])
    }

__all__ = [
    "CATALOG",
    "carregar_catalogo",
    "catalogo_por_area_grau",
    "filtrar",
    "filtrar_por_area_grau",
]
