# InternWorth — Master Project Plan & Build Spec

> This document is the single source of truth for the InternWorth project. It covers the
> problem, the system design, the current state of the code, and the full roadmap from
> prototype to a commercializable product. Use this as the base prompt/context when
> working with a coding agent (e.g. Codex) — it should be enough to build from scratch
> or continue development without additional explanation.

---

## 1. What This Project Is

**InternWorth** is an NLP-driven scoring system that answers one question for a student
looking at an internship posting: **"Is this internship actually worth my time?"**

It analyzes a posting's role description, company information, location, and stated
compensation, and produces an interpretable **Worth Score (0–100)** broken into six
transparent sub-scores — never a single black-box number.

### Problem Statement
Given an internship posting (title, description, company info, location, stipend),
design a system that extracts multiple independent value signals and aggregates them
into a single interpretable Worth Score — without relying on manually curated "worth"
labels, since no such labeled dataset exists at scale.

### Abstract
InternWorth is an NLP-driven composite scoring system that evaluates internship
postings from the candidate's perspective, producing an interpretable Worth Score
(0–100) broken into transparent sub-scores. It combines rule-based extraction, Named
Entity Recognition, sentiment analysis, and (eventually) transformer-based
classification across six independent signal categories, aggregated into one
explainable output. Unlike existing job-posting NLP research — which focuses on fraud
detection or employer-side resume matching — InternWorth targets candidate-side value
assessment, a distinct and underexplored problem.

### SDG Alignment
- **Primary: SDG 8 (Decent Work & Economic Growth)** — targets 8.6 (youth employment
  transition) and 8.8 (protection of labour rights).
- **Secondary: SDG 4 (Quality Education)** — internships are a bridge between education
  and employment.

---

## 2. Why This Is Novel (Research Gap)

Existing NLP-in-hiring research clusters into two saturated areas:
1. **Fraud/scam detection** on job postings (e.g. Kaggle Fake Job Postings dataset,
   95%+ accuracy widely reported) — assumes the job is fake, says nothing about a real
   job's actual value.
2. **Resume ↔ job matching** — optimizes candidate-to-role fit, tells you if you
   qualify, not whether the job is worth taking.

**Nobody scores a real, legitimate posting for candidate-side value.** That's the gap
InternWorth fills. Key literature informing this gap analysis:

| Title | Source | Relevance |
|---|---|---|
| Uncovering Semantic Patterns in Sustainability Research: A Systematic NLP Review | Tashakori et al., Wiley, 2025 | Flags SDG 5 & 10 (social equity) as under-covered in NLP-for-sustainability research |
| NLP for Social Good: A Survey and Outlook of Challenges, Opportunities, and Responsible Deployment | arXiv:2505.22327, 2025 | Decent-work-adjacent domains remain under-researched |
| Fake Job Posting Detection Using Machine Learning and NLP | IJERT, 2024–2026 | Confirms fraud detection is a saturated sub-field |
| Deep Learning-based Computational Job Market Analysis: A Survey on Skill Extraction and Classification | arXiv:2402.05617 | Confirms focus is employer-side, not candidate value |
| JobArabi: An Arabic Corpus and Analysis of Job Announcements from Social Media | arXiv:2605.20960 | Notes fairness auditing in job postings remains underexplored |
| JobRecoGPT — Explainable job recommendations using LLMs | arXiv:2309.11805 | Existing explainable scoring is oriented around resume-job fit, not posting worth |

---

## 3. System Architecture

**This is a real-time, scrape-on-demand system — not a bulk pre-scraped database.**
There is no background scraping job and no large stored corpus of postings. The flow
is: user submits a posting URL → the system fetches that single page live → extracts
fields → scores → returns the result immediately. Nothing is scraped in advance or at
scale.

```
User submits a posting URL
            |
   Real-Time Scraper Module
   (robots.txt check → fetch page → extract fields via CSS selectors)
            |
   Data Preprocessing (cleaning, normalization)
            |
        ------------------------------------------------------
        |         |            |            |         |      |
   Pay/Stipend  Role       Company      Location    PPO /   Red-Flag
   Extractor  Specificity Reputation    Fit         Conv.   Detector
        |         |            |            |         |      |
        ------------------------------------------------------
                              |
                Weighted Score Aggregation Engine
                              |
            InternWorth Score (0–100) + Full Breakdown
                    (returned immediately)
```

### Why Real-Time Instead of Bulk-Scraped
- No large stored dataset means no ongoing scraping infrastructure to maintain, and a
  much smaller legal/ToS footprint — you're fetching one page a user explicitly asked
  about, not crawling a platform at scale.
- Company reputation still benefits from a *cached* lookup (see module table below) so
  repeat lookups of the same company don't require re-scraping review sites every time.
- This also matches the natural product flow: a student pastes in the one posting
  they're actually considering right now and wants an answer immediately.

### Platform Scraping Reality (read before pointing this at any site)
- **LinkedIn and Naukri run active anti-bot detection** and may block the requesting
  IP; LinkedIn specifically has pursued legal action against scrapers at commercial
  scale (*hiQ Labs v. LinkedIn* is the relevant, still-debated precedent).
- **Internshala and smaller/static job boards are far more scraper-tolerant** — prefer
  these for development, testing, and demos.
- Always check `robots.txt` before fetching (the scraper module does this
  automatically and fails closed — i.e. skips the request — if disallowed or
  unreadable).
- Never remove the politeness delay between requests if scoring multiple URLs in a
  loop.

### The Six Signal Modules

| Module | Technique | Output |
|---|---|---|
| Pay / Stipend Extractor | Regex + benchmark comparison against per-city cost-of-living index | Sub-score 0–100 |
| Role Specificity Scorer | Keyword/phrase matching (v1) → sentence-embedding similarity (v2) against a "vague language" reference set | Sub-score 0–100 |
| Company Reputation Module | NER on "About Company" text + sentiment analysis over aggregated public reviews | Sub-score 0–100 |
| Location / Remote-Fit Analyzer | NER location extraction + rule-based consistency check against role type | Sub-score 0–100 |
| PPO / Conversion Detector | Keyword & pattern extraction for pre-placement-offer / full-time-conversion mentions | Sub-score 0–100 (bonus weight) |
| Red-Flag / Exploitation Detector | Rule-based (v1) → trained classifier (v2) on labor-right red-flag language patterns | Penalty factor, inverted into sub-score |

### Scoring Formula

```
Worth Score = 0.25×Pay + 0.20×RoleSpecificity + 0.15×Reputation
            + 0.10×LocationFit + 0.05×Conversion + 0.25×RedFlagAbsence
```

Weights are currently **fixed defaults grounded in labor-fairness reasoning** (pay and
red-flag absence weighted heaviest). They are not yet learned — see Phase 4 below for
the plan to validate/tune them against human ratings.

---

## 4. Current State of the Code (MVP — Already Built)

A working Python prototype already exists with this structure:

```
internworth_mvp/
├── score_url.py                  # REAL-TIME entry point — scrape + score a live URL
├── main.py                       # Offline entry point — scores a sample CSV (testing only)
├── aggregator.py                 # WEIGHTS dict + aggregate() function
├── modules/
│   ├── scraper.py                # Real-time fetcher: robots.txt check, page fetch, field extraction
│   ├── pay_extractor.py          # extract_amount() + score() — regex + cost-of-living lookup
│   ├── role_specificity.py       # score() — vague-phrase vs. concrete-signal keyword matching
│   ├── red_flag_detector.py      # score() — RED_FLAGS pattern dict, penalty-inverted score
│   ├── location_fit.py           # score() — remote/on-site consistency heuristic
│   └── company_and_conversion.py # reputation_score() [placeholder lookup] + conversion_score()
├── data/
│   └── sample_postings.csv       # 6 hand-written sample postings, for offline module testing only
└── requirements.txt              # requests + beautifulsoup4 for scraping; NLP upgrades commented out
```

Every module function returns a dict with at minimum `{"sub_score": int, "note": str}`
so the reasoning behind every number is always human-readable — this explainability
contract must be preserved in all future work.

**Verified working:**
- `python main.py` scores all 6 sample postings end-to-end offline and correctly
  ranks legitimate postings (72–89/100) above exploitative ones (22–42/100).
- `modules/scraper.py`'s extraction logic (`_extract_field`, `_get_profile`) was
  verified against realistic mock HTML matching Internshala's structure — field
  extraction (title, company, location, stipend, description) works correctly.
- `check_robots_allowed()` fails closed (returns `False`/skips scraping) when
  `robots.txt` can't be read or disallows the URL — verified.
- **Not yet verified against a live real-world URL** — the development sandbox this
  was built in cannot reach arbitrary external sites. `SELECTOR_PROFILES` in
  `scraper.py` are best-guess starting points and will very likely need small
  adjustments once run against real, current site HTML (inspect via browser dev
  tools and update the CSS selectors accordingly). This is the first thing to check
  when you pick the project back up.

**Known placeholder / weakest link:** `company_and_conversion.py`'s `reputation_score()`
currently uses a 6-entry hardcoded dict instead of real review data. This is the
highest-priority module to replace with something real.

---

## 5. Build Roadmap

### Phase 1 — Harden the Real-Time Scraper (highest priority right now)
- [ ] Test `modules/scraper.py` against real, live Internshala posting URLs on a
      machine with normal internet access (the original dev sandbox couldn't reach
      external sites). Fix `SELECTOR_PROFILES["internshala.com"]` selectors against
      the actual current HTML.
- [ ] Add 2–3 more `SELECTOR_PROFILES` entries for other scraper-tolerant job boards
      as needed. Do not add LinkedIn/Naukri profiles without accepting the
      blocking/legal risk described in Section 3.
- [ ] Add an in-memory (or simple file/DB-backed) cache keyed by URL so re-scoring the
      same posting doesn't re-fetch the page every time.
- [ ] Add basic retry/backoff handling for transient network failures.
- [ ] Add pytest tests for `scraper.py` using saved mock HTML fixtures (don't hit the
      network in CI).

### Phase 2 — Harden the Scoring Modules
- [ ] Expand `COST_OF_LIVING` in `pay_extractor.py` to cover 25+ Indian cities with a
      real sourced dataset (not hand-guessed numbers).
- [ ] Expand `VAGUE_PHRASES` / `CONCRETE_SIGNALS` in `role_specificity.py` from a
      broader phrase-frequency analysis of real postings.
- [ ] Expand `RED_FLAGS` in `red_flag_detector.py` with more labor-law-grounded
      patterns (research actual Indian labor law red flags, not just guesses).
- [ ] Replace the hardcoded `KNOWN_COMPANY_SCORES` in `company_and_conversion.py` with
      a real pipeline: fetch public company reviews (respecting their robots.txt/ToS
      same as the posting scraper) → run sentiment analysis (start with a HuggingFace
      sentiment pipeline) → cache scores locally so the same company isn't re-fetched
      on every request.
- [ ] Add unit tests for every module covering edge cases: missing data, empty
      strings, unusual formatting.

### Phase 3 — API Layer
- [ ] Wrap `score_live_posting()` (in `score_url.py`) in a **FastAPI** app:
      - `POST /score` — accepts a posting URL, returns Worth Score + breakdown JSON.
      - `GET /health` — deployment readiness check.
- [ ] Add basic input validation (valid URL format, reachable host) and clear error
      responses when scraping is blocked or selectors fail to match.
- [ ] Add a lightweight cache layer (reuse Phase 1's URL cache) at the API level so
      repeated requests for the same URL are instant.

### Phase 4 — Evaluation & Weight Validation
- [ ] Manually rate 20–30 real postings (0–100) using your own judgment + 2–3 other
      raters, to get inter-rater data.
- [ ] Compute Spearman correlation between human ratings and model output
      (`scipy.stats.spearmanr`).
- [ ] Use this data to justify keeping or adjusting the fixed weights in
      `aggregator.py`. If enough labeled data accumulates later, consider training a
      supervised weight-learning model instead of fixed weights.
- [ ] Document all of this as the formal evaluation section for the academic report.

### Phase 5 — Frontend / Demo
- [ ] Build a React + TypeScript frontend (matches existing skill set):
      - A form where the user pastes in a **posting URL**.
      - A results view rendering the Worth Score as a large number + a bar chart of
        the six sub-scores (recharts is fine).
      - Clear loading/error states for when scraping fails or is blocked.
      - Call the FastAPI backend from Phase 3.
- [ ] Deploy backend (Render/Railway free tier is fine for a demo) + frontend
      (Vercel/Netlify) for a live, shareable link.

### Phase 6 — Upgrade NLP Sophistication (optional, after core works end-to-end)
- [ ] Swap `role_specificity.py`'s keyword matching for `sentence-transformers`
      embedding similarity against a curated vague-language reference set.
- [ ] Swap `red_flag_detector.py`'s rule-based matching for a trained classifier
      (needs a labeled dataset built from Phase 1/2 data).
- [ ] Add real NER (spaCy or a fine-tuned transformer) for company/location extraction
      instead of relying on structured CSV fields.

---

## 6. Commercialization & IP Notes

- **Patent (India):** Section 3(k) of the Indian Patents Act excludes pure
  algorithms/business methods from patentability. A pure scoring algorithm is unlikely
  to survive this unless claims are framed around a specific technical implementation,
  not the scoring logic itself. Filing is possible; grant is uncertain.
- **More realistic IP strategy:** treat the exact weighting formula, thresholds, and
  feature-extraction logic as a **trade secret** — keep it server-side, never expose
  the precise weights via the API response in a way that lets someone reverse-engineer
  and clone it exactly.
- **Documentation trail:** keep dated commits / a private repo history as evidence of
  the build timeline, useful if a provisional patent filing is pursued later via the
  college's IPR cell.
- **Data legality:** the architecture is real-time, scrape-on-demand (one page per
  user request, not bulk crawling), which meaningfully reduces — but does not
  eliminate — ToS risk. `robots.txt` is checked before every fetch and the request is
  skipped if disallowed. Still avoid LinkedIn/Naukri at any real scale; prefer
  Internshala and similarly scraper-tolerant sources.
- **Validation before more engineering:** before investing further, cheaply test
  whether real students trust and would use a score like this (show manually-scored
  postings to 10–15 people) — this should happen in parallel with Phase 1/2.

---

## 7. Tech Stack Summary

| Layer | Choice | Status |
|---|---|---|
| Core scoring logic | Python (stdlib only currently) | Built |
| NLP upgrades | spaCy, transformers, sentence-transformers | Planned (Phase 6) |
| Data storage | MySQL/PostgreSQL | Planned (Phase 2) |
| Backend API | FastAPI + uvicorn | Planned (Phase 3) |
| Frontend | React + TypeScript + Tailwind | Planned (Phase 5) |
| Charting | Recharts | Planned (Phase 5) |
| Testing | pytest | Planned (Phase 1) |
| Deployment | Render/Railway (backend), Vercel (frontend) | Planned (Phase 5) |

---

## 8. Instructions for a Coding Agent

If you (the coding agent) are picking this project up:
1. Read `internworth_mvp/` first — it's the working baseline, don't rebuild from
   scratch. `score_url.py` is the primary real-time entry point; `main.py` is an
   offline testing path only.
2. Follow the phases in order — Phase 1 (harden the scraper) before Phase 2 (harden
   scoring modules) before Phase 3 (API), etc. Don't skip ahead to the frontend before
   the scraping + scoring core is solid.
3. Preserve the explainability contract: every module function must keep returning
   `{"sub_score": ..., "note": ...}` at minimum — never collapse to a single opaque
   number.
4. Always check `robots.txt` before fetching any new URL (reuse
   `scraper.check_robots_allowed()`) and fail closed if it can't be verified. Never
   remove this check, and never add scraping logic that bypasses robots.txt or adds
   aggressive concurrency against a single domain.
5. Do not build bulk/background scraping of LinkedIn or Naukri into any code path —
   flag this explicitly if asked, per the risk described in Section 3. New
   `SELECTOR_PROFILES` entries should prioritize scraper-tolerant sites.
6. Keep `aggregator.py`'s `WEIGHTS` as a single, clearly labeled, easily-editable
   source of truth — do not scatter weight logic across modules.
7. When adding a new module or upgrading an existing one, add corresponding pytest
   tests in the same PR/change — for the scraper specifically, use saved mock HTML
   fixtures rather than hitting the network in tests.
