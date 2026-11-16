import pandas as pd

from fugazero import detect, evaluate, simulate


def test_detects_most_leaks_with_few_false_positives():
    df, truth = simulate(n_meters=40, seed=1)
    m = evaluate(detect(df), truth, df.meter_id.unique())
    assert m["recall"] >= 0.9
    assert m["precision"] >= 0.9


def test_no_leaks_no_alerts():
    df, _ = simulate(n_meters=15, leak_fraction=0.0, seed=2)
    assert detect(df).empty


def test_detection_delay_small():
    df, truth = simulate(n_meters=40, seed=3)
    m = evaluate(detect(df), truth, df.meter_id.unique())
    assert m["median_delay_days"] <= 4


def test_output_columns():
    df, _ = simulate(n_meters=5, leak_fraction=1.0, seed=4)
    assert {"meter_id", "leak_start", "leak_lph", "liters_lost"} <= set(detect(df).columns)
