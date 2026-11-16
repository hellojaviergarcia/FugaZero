"""Detección de fugas por análisis del caudal mínimo nocturno (MNF)."""
import numpy as np
import pandas as pd


def night_flow(df: pd.DataFrame, night=(2, 5)) -> pd.DataFrame:
    """Caudal mínimo nocturno diario por contador (L/h)."""
    d = df.assign(hour=df.timestamp.dt.hour, date=df.timestamp.dt.normalize())
    n = d[d.hour.between(*night)]
    return n.groupby(["meter_id", "date"]).liters.min().rename("mnf").reset_index()


def detect(df: pd.DataFrame, ref_days=14, k=5.0, min_excess=3.0, persist=3) -> pd.DataFrame:
    """Devuelve una fila por contador con fuga: inicio estimado, caudal (L/h) y litros perdidos.

    Una fuga = MNF por encima de (mediana de referencia + max(min_excess, k*MAD))
    durante `persist` días seguidos. El caudal de fuga se estima como exceso medio sobre la referencia.
    """
    mnf = night_flow(df)
    out = []
    for m, g in mnf.groupby("meter_id"):
        g = g.sort_values("date").reset_index(drop=True)
        ref = g.mnf.iloc[:ref_days]
        base = ref.median()
        mad = (ref - base).abs().median() * 1.4826
        thr = base + max(min_excess, k * mad)
        flag = (g.mnf > thr).astype(int)
        run = flag.rolling(persist).sum() == persist
        if not run.any():
            continue
        i = int(np.argmax(run.values)) - persist + 1
        start = g.date.iloc[i]
        lph = float((g.mnf.iloc[i:] - base).clip(lower=0).mean())
        hours = (g.date.iloc[-1] - start).days * 24 + 24
        out.append({"meter_id": m, "leak_start": start.date(), "leak_lph": round(lph, 1),
                    "liters_lost": round(lph * hours), "baseline_mnf": round(base, 2)})
    return pd.DataFrame(out, columns=["meter_id", "leak_start", "leak_lph", "liters_lost", "baseline_mnf"])


def evaluate(alerts: pd.DataFrame, truth: pd.DataFrame, all_meters) -> dict:
    """Precisión, recall, retraso de detección (días) y error de caudal contra la verdad-terreno."""
    a, t = set(alerts.meter_id), set(truth.meter_id)
    tp, fp, fn = len(a & t), len(a - t), len(t - a)
    j = alerts.merge(truth, on="meter_id", suffixes=("_det", "_true"))
    delay = (pd.to_datetime(j.leak_start_det) - pd.to_datetime(j.leak_start_true)).dt.days
    return {
        "meters": len(set(all_meters)), "leaks_true": len(t), "alerts": len(a),
        "precision": round(tp / (tp + fp), 3) if tp + fp else 0.0,
        "recall": round(tp / (tp + fn), 3) if tp + fn else 0.0,
        "median_delay_days": float(delay.median()) if len(j) else None,
        "mean_abs_rate_error_lph": round(float((j.leak_lph_det - j.leak_lph_true).abs().mean()), 2) if len(j) else None,
    }
