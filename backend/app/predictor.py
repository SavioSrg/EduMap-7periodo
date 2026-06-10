"""Carregamento do modelo XGBoost e geração de recomendações."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import hashlib
import joblib
import numpy as np
import pandas as pd

from . import catalog_2
from .schemas import CursoRecomendado, PredictRequest, PredictResponse

_MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

_model = joblib.load(_MODELS_DIR / "xgb_model.pkl")
_mapping: Dict[str, Dict] = joblib.load(_MODELS_DIR / "mapping_dict.pkl")

_booster = _model.get_booster()
_FEATURE_NAMES: List[str] = list(_booster.feature_names or [])
_FEATURE_INDEX: Dict[str, int] = {name: i for i, name in enumerate(_FEATURE_NAMES)}
_COURSE_CODES: List[str] = [
    name.replace("CODIGO_CURSO_", "")
    for name in _FEATURE_NAMES
    if name.startswith("CODIGO_CURSO_")
]

_AREA_CLUSTER = {
    "Tecnologia": 1,
    "Engenharias": 2,
    "Saúde": 3,
    "Educação": 4,
    "Negócios": 5,
    "Direito": 6,
}

_MOD_LETRA = {
    "ampla concorrência": "A",
    "ampla concorrencia": "A",
    "cotas": "L",
}


def _code_for(curso_nome: str) -> str:
    if not _COURSE_CODES:
        return ""
    digest = hashlib.md5(curso_nome.encode("utf-8")).digest()
    idx = int.from_bytes(digest[:8], "big") % len(_COURSE_CODES)
    return _COURSE_CODES[idx]


def _grau_t(grau: str) -> int:
    return int(_mapping["GRAU"].get(grau, 0))


def _mod_t(modalidade: str) -> int:
    letra = _MOD_LETRA.get((modalidade or "").strip().lower(), "A")
    return int(_mapping["TIPO_MOD_CONCORRENCIA"].get(letra, 0))


def _build_matrix(req: PredictRequest, cursos: List[Dict]) -> np.ndarray:
    n_feat = len(_FEATURE_NAMES)
    X = np.zeros((len(cursos), n_feat), dtype=np.float32)

    notas = req.notas
    base = {
        "NOTA_L": notas.linguagens,
        "NOTA_CH": notas.humanas,
        "NOTA_CN": notas.natureza,
        "NOTA_M": notas.matematica,
        "NOTA_R": notas.redacao,
        "GRAU_T": _grau_t(req.grau),
        "TIPO_MOD_CONCORRENCIA_T": _mod_t(req.modalidade),
    }

    for col, val in base.items():
        idx = _FEATURE_INDEX.get(col)
        if idx is not None:
            X[:, idx] = float(val)

    for i, curso in enumerate(cursos):
        code = _code_for(curso["nome"])
        col = f"CODIGO_CURSO_{code}"
        idx = _FEATURE_INDEX.get(col)
        if idx is not None:
            X[i, idx] = 1.0

    return X


def predict(req: PredictRequest, top_n: int = 5) -> PredictResponse:
    print("\n\nPREDICT FOI CHAMADO\n\n")
    
    
    print("\n=== REQUEST ===")
    print("interesse:", req.interesse)
    print("grau:", req.grau)
    print("modalidade:", req.modalidade)
    
    cursos = catalog_2.filtrar(req.interesse, req.grau)
    
    print("\n=== RESULTADO DO FILTRO ===")
    print("Quantidade:", len(cursos))

    for c in cursos[:20]:
        print(
            c.get("nome"),
            "| área:",
            c.get("area"),
            "| grau:",
            c.get("grau")
        )
    
    X = _build_matrix(req, cursos)
    df = pd.DataFrame(X, columns=_FEATURE_NAMES)

    try:
        probs = _model.predict_proba(df)[:, 1]
    except Exception:
        import xgboost as xgb

        probs = _model.predict(xgb.DMatrix(df))

    ranked = sorted(zip(cursos, probs), key=lambda t: float(t[1]), reverse=True)[:top_n]
    
    print("\n=== RANKING ===")
    for curso, prob in ranked:
        print(
            curso["nome"],
            "| grau:",
            curso["grau"],
            "| chance:",
            round(float(prob) * 100, 2)
        )

    recomendados = [
        CursoRecomendado(nome=c["nome"], chance=round(float(p) * 100, 1))
        for c, p in ranked
    ]

    perfil = req.interesse or "Geral"
    cluster = _AREA_CLUSTER.get(perfil, 0)

    return PredictResponse(perfil=perfil, cluster=cluster, cursos=recomendados)