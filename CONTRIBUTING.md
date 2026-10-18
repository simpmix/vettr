# Contributing to ARGUS ⬡

We welcome contributions from quantitative analysts, forensic accountants, software engineers, and financial researchers!

## Code Architecture
- `argus/edgar/`: Direct client & parsers for US SEC EDGAR (XBRL, 10-K, 10-Q, 8-K, Form 4).
- `argus/forensics/`: Quantitative forensic models (Beneish M-Score, Altman Z-Score, Piotroski F-Score, DuPont analysis).
- `argus/diff/`: Natural language processing diff engines for year-over-year filing disclosures.
- `argus/screener.py`: Multi-ticker batch anomaly scanner.
- `argus/web/`: FastAPI server and high-density terminal frontend.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/argus.git
   cd argus
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the test suite:
   ```bash
   python -m unittest discover tests/
   ```
4. Launch the local development terminal:
   ```bash
   python run.py
   ```

## Pull Request Guidelines
- Ensure any new forensic model or metric has accompanying unit tests in `tests/`.
- Cite academic literature or authoritative financial accounting standards (e.g. Beneish 1999, Altman 1968, US GAAP ASC standards) when introducing new accounting formulas.
- Maintain compliant SEC EDGAR rate-limiting headers in `argus/config.py`.
