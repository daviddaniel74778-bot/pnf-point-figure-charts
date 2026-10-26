# pnf-point-figure-charts

A minimal **Point & Figure (P&F)** chart renderer in pure Python.

Reads an OHLC CSV, builds classic X/O columns from intraday high/low
movement, and renders as plain text (stdout) or a standalone HTML page.

This is a charting utility only — no signals, no indicators, no advice.

## Install

```bash
pip install requests   # only needed if you pair it with a data fetcher
```

No other dependencies for the core renderer.

## Usage

Generate synthetic sample data (or bring your own OHLC CSV):

```bash
python sample_data.py
```

Render a text chart:

```bash
python pnf.py sample_ohlc.csv --box 100 --reversal 3
```

Render a standalone HTML chart:

```bash
python pnf.py sample_ohlc.csv --box 100 --reversal 3 --html chart.html
```

## Input format

CSV with header columns: `date,open,high,low,close`

```csv
date,open,high,low,close
2024-01-01,42000.00,42350.10,41880.55,42120.30
...
```

## Notes

- Box size and reversal are user parameters; classic default reversal is 3.
- The `sample_data.py` script generates a random walk — it is **not** real
  market data.

## License

MIT
