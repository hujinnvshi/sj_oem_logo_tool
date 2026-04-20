# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OEM Logo Package Production Tool (Secsmart Reskin Tool) — a web-based OEM branding configuration tool that lets partners customize Secsmart product visuals (logos, theme colors, product names) and generate a deployment-ready `oem.zip` package.

**Version:** V3.0.5 | **Branch:** `V3.0.5_ZN_V1.0`

## Running the Server

```bash
# Production (Python HTTP, port 47191, with watchdog)
bash start_server.sh start|stop|restart|status

# Development (Node.js, port 9111, static files only — no API endpoints)
npm start
```

Production access: `http://172.16.48.113:47191`

The watchdog (`watchdog.sh`) runs via cron every 2 minutes, checks HTTP health, and auto-restarts the server if down.

## Architecture

This is a **dual-layer application** with no build system — all JS/CSS bundles are pre-built and served as static files. The only editable source code is `assets/main.html`.

### Layer 1: React Preview Shell (`index.html` → `js/app.js`)

The entry point loads a React SPA (pre-built Webpack bundle) that provides a simulated product interface with sidebar, header, and preview modals. It embeds the OEM form as an **iframe** pointing to `assets/main.html`.

Communication uses `window.postMessage()`:
- iframe → parent: `oemDataUpdate` (field changes), `showModal` (layout preview), `loginPreview` (login preview)
- Shared state via `sessionStorage` (keys: `_personalizedData`, `_theme`, `_pageType`, `_modalVisible`)

### Layer 2: OEM Configuration Form (`assets/main.html`)

A standalone vanilla HTML/JS page (~1815 lines) that is the **core of all OEM functionality**. Contains its own CSS (`oem.css`, Font Awesome) and libraries (JSZip, SheetJS). Key areas:

- **Sidebar library:** Left panel showing vendor→product tree from `OEM_ZIYUAN/`. Clicking a product auto-fills the form with its xlsx config + images. Defaults to open on page load.
- **Theme selector:** 17 themes defined in `THEMES` array
- **Image uploads:** 6 slots with validation (dimensions, size, format, 10% tolerance) defined in `IMAGE_REQUIREMENTS` and `FILENAME_MAP`. SVG images skip dimension validation.
- **Product info:** 9 text fields stored in `userInput` object. When `生产厂商` is empty (白牌 mode), three product name fields auto-sync.
- **License agreements:** File uploads with metadata stored in `licenseFiles`
- **Output:** `generateOemPackage()` creates `oem.zip` containing `oem/oeminfo.xlsx` + `oem/images/` + `oem/files/`

### Key Data Structures in `assets/main.html`

| Variable | Purpose |
|----------|---------|
| `MOCK_ROWS` | Template rows defining all form fields and their defaults |
| `userInput` | Current form values (keyed by Chinese field names) |
| `uploadedFiles` / `reconstructedFiles` | Uploaded images and images rebuilt from sessionStorage |
| `licenseFiles` / `reconstructedLicenseFiles` | License agreement files |
| `imagesBase64Data` | Base64-encoded image previews in sessionStorage |
| `FILENAME_MAP` | Maps image slot names to canonical output filenames |
| `IMAGE_REQUIREMENTS` | Dimension/size constraints per image slot |
| `libraryData` | Cached response from `/api/library` (vendor/product tree) |

### Key Functions in `assets/main.html`

| Function | Line | Purpose |
|----------|------|---------|
| `renderForm()` | ~952 | Builds entire form UI from `MOCK_ROWS` |
| `createFormItem()` | ~285 | Creates individual form controls (text input, file upload, select) |
| `saveDataToSessionStorage()` | ~1012 | Persists form data + builds `personalizedData` for React shell |
| `generateOemPackage()` | ~1203 | Creates `oem.zip` with JSZip, triggers download, archives to server |
| `importOemPackage()` | ~1101 | Reads existing `oem.zip`, parses xlsx/images, restores form |
| `restoreDefaults()` | ~1345 | Clears all data, loads default images, reloads page |
| `initSidebar()` | ~1791 | Binds Escape key, calls `openSidebar()` on page load |
| `loadLibraryData()` | ~1565 | Fetches `/api/library`, caches to `libraryData`, renders tree |
| `renderTree()` | ~1579 | Renders vendor→product tree (default expanded) |
| `filterTree()` | ~1619 | Search filter for vendor/product names |
| `selectProduct()` | ~1658 | Click product → fetch xlsx + images → fill form → reload |

### Server-Side: `server.py`

Python 3 HTTP server on port 47191. In addition to static file serving:
- **GET `/api/library`** — Scans `OEM_ZIYUAN/` and returns vendor/product tree as JSON (used by sidebar)
- **POST `/api/save`** — Receives base64-encoded oem.zip, extracts to `OEM_ZIYUAN/<manufacturer>/` with MD5-based image deduplication
- **POST `/api/save-preview`** — Saves preview screenshots to `OEM_ZIYUAN/<manufacturer>/previews/`
- These API endpoints are only available in production mode (not `npm start`)

### OEM_ZIYUAN Directory

Server-side archive of generated OEM packages, organized by manufacturer name. When `生产厂商` is empty, the archive directory is named `白牌`. Structure per vendor: `<Product>_oeminfo.xlsx`, `images/`, `files/`, `previews/`.

### State Flow

1. Page loads → sidebar opens by default, fetches `/api/library` to populate vendor/product tree
2. User edits form (manually or by selecting a product from sidebar) → triggers `saveDataToSessionStorage()`
3. Every change sends `postMessage({type: 'oemDataUpdate'})` to React parent
4. React shell reads `_theme` and `_personalizedData` from sessionStorage for preview rendering
5. "Generate oem.zip" → iframe uses JSZip + SheetJS to create and download the package, then POSTs to `/api/save` for server-side archiving
6. Preview buttons → iframe sends `postMessage` to React parent, which opens modal previews using stored data
7. Sidebar `selectProduct()` → fetches xlsx + images from `OEM_ZIYUAN/<vendor>/`, fills form, saves to sessionStorage, reloads page

### File Map

| Path | Purpose |
|------|---------|
| `index.html` | Entry point, loads React shell |
| `js/vendors.js` | React, ReactDOM, Ant Design (pre-built, not rebuildable) |
| `js/app.js` | React SPA application (pre-built, not rebuildable) |
| `assets/main.html` | **OEM config form — the only file to modify for form changes** |
| `assets/oem.css` | Form styling |
| `assets/xlsx.full.min.js` | SheetJS for Excel generation |
| `assets/jszip.min.js` | JSZip for ZIP creation |
| `server.py` | Python production server with archive API |
| `start_server.sh` | Production server start/stop/restart script |
| `watchdog.sh` | Cron-based health check and auto-restart |
| `images/` | Default brand assets (14 files) |
| `OEM_ZIYUAN/` | Server-side archive of generated OEM packages |

## Important Notes

- **No build/test/lint pipeline exists.** The `js/app.js` and `js/vendors.js` bundles were built externally and are not rebuildable from this repository.
- The functional code lives entirely in `assets/main.html` — that is the file to modify for OEM form changes.
- Theme changes in the React shell trigger `location.reload()` rather than hot updates.
- All images must conform to sizes defined in `IMAGE_REQUIREMENTS` with filenames mapped by `FILENAME_MAP`. SVG images bypass dimension checks.
- Generated zip filename format: `<date>_<manufacturer|白牌>_<product|oem>_oem.zip`
- After modifying `assets/main.html`, restart the production server with `bash start_server.sh restart` to pick up changes.
- Preview buttons (主界面预览/登录页预览) only work when accessed through the parent page (`/`), not directly via `/assets/main.html`, because the React shell is needed to handle `postMessage` events.
