# FugaZero

Detección de fugas de agua mediante análisis del **caudal mínimo nocturno (MNF)** de contadores inteligentes. Pensado para comunidades de regantes, hoteles y redes municipales en Canarias.

**ODS:** 6 (agua), 9 (infraestructura), 11 (ciudades), 12 (consumo responsable), 13 (clima).

## Por qué
Cada litro perdido en una isla es agua desalada (energía + CO₂). De madrugada el consumo legítimo es casi nulo, así que un caudal nocturno persistente delata una fuga. FugaZero la detecta, estima su inicio, caudal (L/h) y el agua/coste perdido, solo con lecturas horarias (sin sensores ni drones nuevos).

## Uso
```bash
python -m venv .venv
.venv\Scripts\activate                         # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
python -m fugazero demo                        # simula 20 contadores y valida
python -m fugazero detect data/lecturas_ejemplo.csv   # CSV: timestamp,meter_id,liters
pytest
```
Salida en `outputs/`: `alertas.csv` e `informe.md`.

## Método
1. MNF diario por contador (mínimo de 2:00 a 5:00).
2. Línea base robusta: mediana y MAD de los primeros 14 días.
3. Alerta si el MNF supera `base + max(3, 5·MAD)` durante 3 días seguidos.
4. Caudal de fuga = exceso medio sobre la base; pérdida = caudal × horas.

## Validación (datos simulados, `python -m fugazero demo`)
| Métrica | Valor |
|---|---|
| Precisión | 1.00 |
| Recall | 1.00 |
| Retraso mediano | 0 días |
| Error medio de caudal | 0.83 L/h |

> Resultados sobre datos sintéticos; la validación con datos reales (piloto) está en la hoja de ruta.

## Hoja de ruta
- [ ] Piloto con lecturas reales (ayuntamiento / comunidad de regantes / hotel)
- [ ] Validación con BattLeDIM
- [ ] Panel web (Streamlit) y alertas por email/Telegram
- [ ] Corrección por estacionalidad y consumo nocturno legítimo (riego, piscinas)

## Licencia
MIT
