# InternWorth

An explainable, candidate-first internship evaluator. Paste a listing URL for a polite, real-time single-page analysis, or enter the information manually when a website cannot be read.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000`.

## API

- `POST /score` with `{ "url": "https://..." }` fetches one live listing after a robots.txt check. Results are cached for 15 minutes.
- `POST /score/manual` accepts `title`, `company`, `location`, `stipend`, `description`, and optional `company_info`.
- `POST /score/file` accepts a single PDF, Word `.docx`, PNG, JPG, or WEBP listing (maximum 10 MB). PDFs and DOCX files are read natively; screenshots and scanned PDFs use OCR if Tesseract is installed on the server.
- `GET /health` provides a basic deployment health check.

The scoring weights live together in `aggregator.py`. Every signal returns a sub-score and a plain-language note so no result is a black box.

## Scope and safeguards

The app does not crawl platforms or scrape in the background. It fetches only the user-selected URL and fails closed when robots.txt cannot be read or denies access. When extraction is blocked, the UI directs users to manual entry.
