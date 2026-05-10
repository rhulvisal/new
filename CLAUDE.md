# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a **Facebook Phone Number Checker API** that determines if phone numbers are registered on Facebook. It uses Tor for IP rotation to avoid rate limiting and stores results in Supabase.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Docker                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Tor Proxy  │  │   Rotator   │  │    FastAPI Server   │  │
│  │   (9050)    │  │   (Python)  │  │      (port 8000)     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
              │                                    │
              ▼                                    ▼
         Control Port                          Supabase
           (9051)                              Database
```

- **Tor** (port 9050): SOCKS5 proxy for IP rotation
- **rotator.py**: Signals Tor to build new circuits every 10 seconds
- **main.py**: FastAPI app with `/check`, `/test`, and `/result/{task_id}` endpoints

## Running

```bash
# Build and run with Docker
docker build -t fb-checker .
docker run -p 8000:8000 fb-checker

# Or use Railway (configured in railway.json)
```

## Key Patterns

**Token Extraction** (main.py:156-256): Parses Facebook's `__bkv`, `rev`, `dtsg`, `lsd` from the identify page HTML using regex patterns. These tokens are required for the search API.

**Search Request** (main.py:299-366): Builds the POST payload to `https://m.facebook.com/async/wbloks/fetch/` with nested JSON params containing the phone number.

**Response Parsing** (main.py:369-492): Analyzes the JSON response for indicators like `push_screen_BloksCAAAccountRecoveryAuthMethodController` (account found) or `search_error_dialog_shown` (not found).

**IP Rotation**: Rotator signals `Signal.NEWNYM` to Tor's control port, which forces a new circuit. MaxCircuitDirtiness is set to 10 seconds.

## Configuration

- Tor control cookie: `/var/lib/tor/control_auth_cookie`
- Supabase table: `fb_checks` (columns: number, registered, checked_at)
- Worker count auto-calculated from RAM: `RAM_GB * 3` (max 24)