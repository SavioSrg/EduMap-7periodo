"""Catálogo curado de cursos por área de interesse.

Cada curso define:
- nome
- area (alinhada às opções da Etapa 2 do frontend)
- grau (Bacharelado | Licenciatura | Tecnológico)
- pesos das 5 provas do ENEM (NOTA_L, NOTA_CH, NOTA_CN, NOTA_M, NOTA_R)
- nota_corte média estimada (escala 0-1000)

Os valores são plausíveis para SISU 2023 e servem como ponto de partida.
Substitua por dados oficiais do MEC para produção.
"""
from typing import List, Dict

# Pesos padrão por área (L, CH, CN, M, R)
_PESOS = {
    "tec": (1.0, 1.0, 1.5, 2.0, 1.5),
    "eng": (1.0, 1.0, 2.0, 2.0, 1.0),
    "sau": (1.0, 1.0, 2.0, 1.5, 1.5),
    "edu": (1.5, 2.0, 1.0, 1.0, 1.5),
    "neg": (1.5, 1.5, 1.0, 2.0, 1.5),
    "dir": (2.0, 2.0, 1.0, 1.0, 2.0),
}

CATALOG: List[Dict] = [
    # Tecnologia
    {"nome": "Ciência da Computação",      "area": "Tecnologia",  "grau": "Bacharelado",  "pesos": _PESOS["tec"], "nota_corte": 720},
    {"nome": "Sistemas de Informação",     "area": "Tecnologia",  "grau": "Bacharelado",  "pesos": _PESOS["tec"], "nota_corte": 680},
    {"nome": "Engenharia de Software",     "area": "Tecnologia",  "grau": "Bacharelado",  "pesos": _PESOS["tec"], "nota_corte": 710},
    {"nome": "Análise e Desenvolvimento de Sistemas", "area": "Tecnologia", "grau": "Tecnológico", "pesos": _PESOS["tec"], "nota_corte": 640},
    {"nome": "Ciência de Dados",           "area": "Tecnologia",  "grau": "Bacharelado",  "pesos": _PESOS["tec"], "nota_corte": 730},
    {"nome": "Redes de Computadores",      "area": "Tecnologia",  "grau": "Tecnológico",  "pesos": _PESOS["tec"], "nota_corte": 620},

    # Engenharias
    {"nome": "Engenharia Civil",           "area": "Engenharias", "grau": "Bacharelado",  "pesos": _PESOS["eng"], "nota_corte": 700},
    {"nome": "Engenharia Mecânica",        "area": "Engenharias", "grau": "Bacharelado",  "pesos": _PESOS["eng"], "nota_corte": 710},
    {"nome": "Engenharia Elétrica",        "area": "Engenharias", "grau": "Bacharelado",  "pesos": _PESOS["eng"], "nota_corte": 720},
    {"nome": "Engenharia de Produção",     "area": "Engenharias", "grau": "Bacharelado",  "pesos": _PESOS["eng"], "nota_corte": 690},
    {"nome": "Engenharia Química",         "area": "Engenharias", "grau": "Bacharelado",  "pesos": _PESOS["eng"], "nota_corte": 705},
    {"nome": "Engenharia Ambiental",       "area": "Engenharias", "grau": "Bacharelado",  "pesos": _PESOS["eng"], "nota_corte": 670},
    {"nome": "Engenharia de Controle e Automação", "area": "Engenharias", "grau": "Tecnológico", "pesos": _PESOS["eng"], "nota_corte": 660},

    # Saúde
    {"nome": "Medicina",                   "area": "Saúde",       "grau": "Bacharelado",  "pesos": _PESOS["sau"], "nota_corte": 820},
    {"nome": "Enfermagem",                 "area": "Saúde",       "grau": "Bacharelado",  "pesos": _PESOS["sau"], "nota_corte": 660},
    {"nome": "Odontologia",                "area": "Saúde",       "grau": "Bacharelado",  "pesos": _PESOS["sau"], "nota_corte": 720},
    {"nome": "Fisioterapia",               "area": "Saúde",       "grau": "Bacharelado",  "pesos": _PESOS["sau"], "nota_corte": 680},
    {"nome": "Farmácia",                   "area": "Saúde",       "grau": "Bacharelado",  "pesos": _PESOS["sau"], "nota_corte": 690},
    {"nome": "Nutrição",                   "area": "Saúde",       "grau": "Bacharelado",  "pesos": _PESOS["sau"], "nota_corte": 660},
    {"nome": "Psicologia",                 "area": "Saúde",       "grau": "Bacharelado",  "pesos": _PESOS["sau"], "nota_corte": 700},
    {"nome": "Estética e Cosmética",       "area": "Saúde",       "grau": "Tecnológico",  "pesos": _PESOS["sau"], "nota_corte": 600},

    # Educação
    {"nome": "Pedagogia",                  "area": "Educação",    "grau": "Licenciatura", "pesos": _PESOS["edu"], "nota_corte": 600},
    {"nome": "Letras - Português",         "area": "Educação",    "grau": "Licenciatura", "pesos": _PESOS["edu"], "nota_corte": 610},
    {"nome": "Letras - Inglês",            "area": "Educação",    "grau": "Licenciatura", "pesos": _PESOS["edu"], "nota_corte": 620},
    {"nome": "História",                   "area": "Educação",    "grau": "Licenciatura", "pesos": _PESOS["edu"], "nota_corte": 630},
    {"nome": "Geografia",                  "area": "Educação",    "grau": "Licenciatura", "pesos": _PESOS["edu"], "nota_corte": 615},
    {"nome": "Matemática",                 "area": "Educação",    "grau": "Licenciatura", "pesos": _PESOS["edu"], "nota_corte": 640},
    {"nome": "Biologia",                   "area": "Educação",    "grau": "Licenciatura", "pesos": _PESOS["edu"], "nota_corte": 635},
    {"nome": "Educação Física",            "area": "Educação",    "grau": "Licenciatura", "pesos": _PESOS["edu"], "nota_corte": 620},

    # Negócios
    {"nome": "Administração",              "area": "Negócios",    "grau": "Bacharelado",  "pesos": _PESOS["neg"], "nota_corte": 660},
    {"nome": "Ciências Contábeis",         "area": "Negócios",    "grau": "Bacharelado",  "pesos": _PESOS["neg"], "nota_corte": 650},
    {"nome": "Ciências Econômicas",        "area": "Negócios",    "grau": "Bacharelado",  "pesos": _PESOS["neg"], "nota_corte": 680},
    {"nome": "Marketing",                  "area": "Negócios",    "grau": "Tecnológico",  "pesos": _PESOS["neg"], "nota_corte": 620},
    {"nome": "Gestão Comercial",           "area": "Negócios",    "grau": "Tecnológico",  "pesos": _PESOS["neg"], "nota_corte": 600},
    {"nome": "Logística",                  "area": "Negócios",    "grau": "Tecnológico",  "pesos": _PESOS["neg"], "nota_corte": 590},
    {"nome": "Comércio Exterior",          "area": "Negócios",    "grau": "Tecnológico",  "pesos": _PESOS["neg"], "nota_corte": 610},

    # Direito
    {"nome": "Direito",                    "area": "Direito",     "grau": "Bacharelado",  "pesos": _PESOS["dir"], "nota_corte": 720},
    {"nome": "Relações Internacionais",    "area": "Direito",     "grau": "Bacharelado",  "pesos": _PESOS["dir"], "nota_corte": 700},
    {"nome": "Ciências Sociais",           "area": "Direito",     "grau": "Bacharelado",  "pesos": _PESOS["dir"], "nota_corte": 670},
    {"nome": "Serviço Social",             "area": "Direito",     "grau": "Bacharelado",  "pesos": _PESOS["dir"], "nota_corte": 640},
]


def filtrar(area: str, grau: str) -> List[Dict]:
    """Retorna cursos do catálogo filtrados por área e grau.

    Se ``area`` for vazia ou "Não tenho preferência", todas as áreas entram.
    """
    pool = CATALOG
    if area and area.lower() not in ("", "não tenho preferência", "nao tenho preferencia"):
        pool = [c for c in pool if c["area"].lower() == area.lower()]
    if grau:
        pool = [c for c in pool if c["grau"].lower() == grau.lower()]
    # Fallback: se nenhum match, devolve toda a área (ignora grau).
    if not pool and area:
        pool = [c for c in CATALOG if c["area"].lower() == area.lower()]
    if not pool:
        pool = CATALOG
    return pool