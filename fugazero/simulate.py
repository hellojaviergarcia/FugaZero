"""Generador de lecturas horarias sintéticas con fugas inyectadas (con verdad-terreno)."""
import numpy as np
import pandas as pd


def simulate(n_meters=20, days=90, leak_fraction=0.3, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2026-01-01", periods=days * 24, freq="h")
    hour = idx.hour.values
    # perfil diario: picos mañana y tarde, mínimo nocturno bajo
    profile = (0.2 + np.exp(-((hour - 8) ** 2) / 8) + 0.8 * np.exp(-((hour - 20) ** 2) / 10))
    rows, truth = [], []
    for m in range(n_meters):
        scale = rng.uniform(20, 120)
        liters = np.clip(profile * scale * rng.normal(1, 0.15, len(idx)), 0, None)
        liters[(hour >= 2) & (hour <= 5)] *= rng.uniform(0.02, 0.1)
        has_leak = rng.random() < leak_fraction
        if has_leak:
            start = int(rng.integers(20, days - 15))
            rate = rng.uniform(8, 40)  # litros/hora constantes
            liters[start * 24:] += rate * rng.normal(1, 0.05, len(idx) - start * 24)
            truth.append({"meter_id": f"M{m:03d}", "leak_start": idx[start * 24].date(), "leak_lph": round(rate, 1)})
        rows.append(pd.DataFrame({"timestamp": idx, "meter_id": f"M{m:03d}", "liters": liters.round(2)}))
    return pd.concat(rows, ignore_index=True), pd.DataFrame(truth, columns=["meter_id", "leak_start", "leak_lph"])
