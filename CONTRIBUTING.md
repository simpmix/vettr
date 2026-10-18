# Contributing to VETTR

We welcome contributions from quantitative analysts, forensic accountants, systems engineers, and financial researchers.

## Architecture

- `vettr/edgar/`: SEC EDGAR API clients, XBRL GAAP parsers, Form 4 insider scrapers, rate limiting.
- `vettr/forensics/`: Quantitative forensic models (Beneish M-Score, Altman Z-Score, Piotroski F-Score, DuPont decomposition, Loughran-McDonald NLP).
- `vettr/diff/`: Natural language processing diff engines for year-over-year filing disclosures.
- `vettr/screener.py`: Multi-ticker batch anomaly scanner.
- `vettr/web/`: FastAPI server and Swiss-brutalist financial workstation.

## Development Setup

1. Clone repository:
   ```bash
   git clone https://github.com/simpmix/vettr.git
   cd vettr
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run test suite:
   ```bash
   python -m unittest discover tests/
   ```
4. Launch local workstation:
   ```bash
   python run.py
   ```

## PR Protocols
- All formula modifications must include unit test coverage in `tests/test_metrics.py`.
- Cite academic literature or authoritative US GAAP ASC standards when introducing new metrics.
