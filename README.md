# ASTRAL - AI-Powered Job Scraping & Analysis

Automated job board scraping with AI-generated parsers + intelligent fit analysis.

## What It Does

1. **AI Parser Generation**: Point at any job board → AI generates custom parser
2. **Smart Scraping**: Handles pagination automatically (buttons, links, infinite scroll)
3. **Job Analysis**: Claude analyzes job fit against your resume and preferences
4. **Web UI**: Manage configs, curate jobs, view analysis results

## Quick Start

```bash
# Activate venv
source .venv/bin/activate

# Generate parser for a job board
python3 src/astral_discover.py debug/sliceinput.json --config-name my_board

# Scrape jobs
python3 src/astral_scraper.py my_board

# Analyze jobs (after curating in UI)
python3 src/astral_consult.py --input results/astral_review.json
```

## Shell Scripts

Convenience scripts for running common gazer operations:

### `gazer_watchlist.sh`
Runs companies from the "watch" category that haven't been searched in 24+ hours.

**Usage:**
```bash
./gazer_watchlist.sh [--p N|--pipeline N] [--b M|--batchcount M] [--f|--foreground] [--d|--debug]
```

**Parameters:**
- `--p N` or `--pipeline N` - Number of companies to run concurrently (default: 1)
- `--b M` or `--batchcount M` - Number of batches to process (default: 0 = all)
- `--f` or `--foreground` - Run in foreground instead of background
- `--d` or `--debug` - Enable debug logging (shows jobSite and jobTag for each company)

**Examples:**
```bash
# Run with defaults (1 concurrent, all batches)
./gazer_watchlist.sh

# Run with 3 concurrent companies (short flags)
./gazer_watchlist.sh --p 3

# Run with 3 concurrent companies (long flags)
./gazer_watchlist.sh --pipeline 3

# Run only 2 batches (6 companies if pipeline=3)
./gazer_watchlist.sh --p 3 --b 2

# Run in foreground to see output directly
./gazer_watchlist.sh --p 2 --f
```

**Output:** Logs to `logs/watchlist.log` (or stdout if `--foreground`)

---

### `gazer_new.sh`
Runs companies from the "new" category with configurable concurrency and batch limits.

**Usage:**
```bash
./gazer_new.sh [--p N|--pipeline N] [--b M|--batchcount M] [--f|--foreground]
```

**Parameters:**
- `--p N` or `--pipeline N` - Number of companies to run concurrently (default: 3)
- `--b M` or `--batchcount M` - Number of batches to process (default: 0 = all)
- `--f` or `--foreground` - Run in foreground instead of background

**Examples:**
```bash
# Run with defaults (3 concurrent, all batches)
./gazer_new.sh

# Run with 5 concurrent companies (short flags)
./gazer_new.sh --p 5

# Run with 5 concurrent companies (long flags)
./gazer_new.sh --pipeline 5

# Run only 2 batches (6 companies if pipeline=3)
./gazer_new.sh --p 3 --b 2

# Run in foreground to see output directly
./gazer_new.sh --p 2 --f
```

**Output:** Logs to `logs/new.log` (or stdout if `--foreground`)

---

### `gazer_company.sh`
Runs a single company by short name.

**Usage:**
```bash
./gazer_company.sh <company_shortname>
```

**Parameters:**
- Company short name (required)

**Example:**
```bash
./gazer_company.sh thoughtfulai
```

**Output:** Logs to `logs/gazer_<company>.log`

---

### `gazer_url.sh`
Runs a single company by URL.

**Usage:**
```bash
./gazer_url.sh <url> [company_shortname]
```

**Parameters:**
- URL (required) - Job board URL to scrape
- Company short name (optional) - For logging purposes

**Example:**
```bash
./gazer_url.sh https://boards.greenhouse.io/thoughtful thoughtfulai
```

**Output:** Logs to `logs/gazer_<company>.log` or `logs/gazer_unknown.log`

---

### `caffeinate_service.sh`
Utility script for keeping the system awake during long-running processes.

**Usage:**
```bash
./caffeinate_service.sh
```

**Parameters:** None

**Note:** All gazer scripts use `caffeinate` internally, so this script is rarely needed directly.

## Project Structure

```
astral/
├── src/                      # Core modules
│   ├── astral_discover.py    # AI parser generation
│   ├── astral_parser.py      # Parser management (THE HINGE)
│   ├── astral_scraper.py     # Job scraping engine
│   ├── astral_consult.py     # AI job fit analysis
│   ├── astral_saver.py       # Deduplication & storage
│   └── astral_library.py     # Config management
├── boards/                   # Board configs (NEW STRUCTURE)
│   └── <board_name>/
│       ├── config.json       # Board metadata
│       ├── parser.py         # AI-generated parser
│       ├── loader.py         # AI-generated loader
│       └── README.md         # Board notes
├── ui/                       # Flask web interface
│   ├── app.py
│   ├── templates/
│   └── static/
├── analysis/                 # Data pipeline (will be renamed from results/)
│   ├── astral_ingress.json   # All scraped jobs (with body)
│   ├── astral_consult.json   # Sent to Gladys for analysis (with body)
│   ├── astral_feedback.json  # Gladys's recommendations (no body)
│   ├── astral_graduate.json  # Approved applications (no body)
│   └── astral_index.json     # Master lifecycle tracker (no body)
├── docs/                     # All documentation
│   ├── Design_Astral_AI_Recruiting.md
│   ├── QUICK_START.md
│   ├── resumes/              # Your resume & preferences
│   │   ├── base_content.txt
│   │   └── preferences.txt
│   └── ...
└── README.md                 # This file
```

## How It Works

### 1. Discovery (Generate Parser)
```bash
python3 src/astral_discover.py debug/sliceinput_myboard.json --config-name myboard
```

- Fetches HTML from job board
- Sends to Anthropic API
- AI generates custom parser for that board's structure
- Validates "while you wait"
- Saves to `boards/myboard/parser.py`

### 2. Scraping (Use Parser)
```bash
python3 src/astral_scraper.py myboard
```

- Loads AI-generated parser
- Navigates to job board
- Handles pagination automatically
- Extracts job data
- Saves to `results/astral_ingress.json`

### 3. Analysis (AI Fit Scoring)
```bash
# Via Web UI: Select jobs for analysis
# Then run:
python3 src/astral_consult.py --input results/astral_review.json
```

- Analyzes jobs against your resume
- Scores technical, cultural, trajectory fit
- Provides recommendations (APPLY/MAYBE/PASS)
- For 80%+ fits: resume tweaks, cover letter points, research tasks

## Web UI

```bash
python3 ui/app.py
# Visit http://localhost:5000
```

**Pages:**
- `/` - Config management
- `/batch-prep` - Select jobs for analysis
- `/results` - View AI analysis results

## State machines

### Job state machine (posting table)

Defined in `src/utils/config.py`: `job_states` and `job_state_transitions`. Consult uses these for analysis workflow; Tracker does not. States are UPPERCASE (e.g. INDEXED, PASSED_GET, FAILED_LIKE, LEGACY).

### Company state machine (company table)

Defined in `src/utils/config.py`: **company_states** and **company_state_transitions**. Roster flows use these; states are UPPERCASE in the DB. All roster flows use state only (no "nodes"); e.g. IGNORE is a state, not a separate bucket. **Single source of truth:** add or change company states only in config.py.

Schema and blob shapes (company_data, agent_responses, parse_instructions, snake_case): see `docs/ROSTER_DATA_MODEL.md`.

## Documentation

See `docs/` directory for:
- Complete system design
- Architecture details
- Implementation guides
- Development notes
- **Roster data model** (`docs/ROSTER_DATA_MODEL.md`) — company schema, company_data vs agent_responses, parse_instructions, prompt-index keys

## Legacy Directory

- `x_heavybit/` - Old single-board scraper (deprecated, to be removed)

## Requirements

```bash
pip install anthropic beautifulsoup4 flask playwright
playwright install firefox
```

Set environment variable:
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

## Credits

Built by Chuckles with guidance from Vern and direction from Susan.

AI-powered parser generation uses Anthropic's Claude Sonnet 4.
