# Astral Gazer

The recurring job board scanner. Gazer watches the careers pages of companies that Roster has qualified and keeps the job inventory current by scraping, parsing, and deduplicating listings on a configurable schedule.

## Role in the System

Roster finds and qualifies company job pages. Gazer takes over from there — it periodically revisits those pages, extracts the current job listings, and feeds them into Tracker for deduplication and storage. Consult then evaluates the jobs Tracker has ingested. Gazer is the heartbeat that keeps the pipeline fed with fresh data.

Without Gazer, the system has a one-time snapshot of each company's job page from the moment Roster discovered it. Gazer turns that into a living inventory — detecting new postings, confirming existing ones are still active, and recording scan outcomes for monitoring.

## How It Works

Gazer runs in batch cycles. Each cycle claims a set of companies due for scanning (prioritizing those never scanned, then those scanned longest ago), scrapes their job pages using Playwright, extracts individual job listings from the DOM using CSS selectors the system has previously learned, and hands the raw HTML to Tracker for ingestion. Every scan outcome — success or failure, jobs found or not — is recorded to an audit table for lineage tracking and monitoring.

When a company has been scraped before, Gazer reuses the stored parse instructions (container and job_tag selectors). When encountering a company for the first time post-Roster, Gazer falls back to AI-driven parsing to discover the selectors, then persists them for future scans. This means the first scan is expensive (AI call) but every subsequent scan is cheap (pure DOM extraction).

## What It Touches

- **Roster** provides the qualified companies and their job site URLs. Gazer inherits Roster's parse logic for first-time selector discovery.
- **Tracker** receives the extracted job listings for deduplication and storage. Gazer passes raw HTML; Tracker handles content hashing and state management.
- **Dispatcher** schedules Gazer batch runs at configured intervals and tracks execution outcomes.
- **Foundation** provides the browser automation (Playwright), batch claiming primitives (database), and scan audit recording.

## Design Principles

- **Cheap by default** — AI calls only happen when parse instructions don't exist yet. Steady-state scanning is pure DOM extraction with no API cost.
- **Fault-tolerant** — Scrape failures, parse failures, and ingestion failures are all recorded but don't poison the batch. Failed companies stay in their scanning state for retry on the next cycle.
- **Full audit trail** — Every scan is recorded with batch_id, timestamps, job counts, and failure details. The batch_id links scan records to the jobs created from that scan, providing complete lineage from discovery to evaluation.
