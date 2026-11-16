"""Uso:
  python -m fugazero demo [--out outputs]
  python -m fugazero detect lecturas.csv [--out outputs]   # CSV: timestamp,meter_id,liters
"""
import argparse
import json
from pathlib import Path

import pandas as pd

from .detect import detect, evaluate
from .simulate import simulate

PRICE_EUR_M3 = 2.0  # coste medio orientativo del agua (editable)


def _write(alerts, out, metrics=None):
    out.mkdir(parents=True, exist_ok=True)
    alerts = alerts.assign(eur_lost=(alerts.liters_lost / 1000 * PRICE_EUR_M3).round(2))
    alerts.to_csv(out / "alertas.csv", index=False)
    lines = ["# Informe FugaZero", "", f"Fugas detectadas: **{len(alerts)}**",
             f"Agua perdida estimada: **{alerts.liters_lost.sum() / 1000:.1f} m³** (~{alerts.eur_lost.sum():.0f} €)", ""]
    if metrics:
        lines += ["## Validación (datos simulados)", "```json", json.dumps(metrics, indent=2), "```"]
    (out / "informe.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


def main():
    p = argparse.ArgumentParser(prog="fugazero")
    p.add_argument("cmd", choices=["demo", "detect"])
    p.add_argument("csv", nargs="?")
    p.add_argument("--out", default="outputs")
    a = p.parse_args()
    out = Path(a.out)
    if a.cmd == "demo":
        df, truth = simulate()
        alerts = detect(df)
        _write(alerts, out, evaluate(alerts, truth, df.meter_id.unique()))
    else:
        if not a.csv:
            p.error("detect requiere un CSV")
        if not Path(a.csv).is_file():
            p.error(f"no existe {a.csv}. Prueba con data/lecturas_ejemplo.csv")
        df = pd.read_csv(a.csv, parse_dates=["timestamp"])
        _write(detect(df), out)


if __name__ == "__main__":
    main()
