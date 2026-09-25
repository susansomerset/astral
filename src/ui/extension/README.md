# Astral Surfer — browser extension

WXT Manifest V3 empty shell (`AST-1254`). Auth and capture land in sibling tickets.

## Install

```bash
cd src/ui/extension
npm install
```

## Chrome — load unpacked

```bash
npm run build
```

Then Chrome → `chrome://extensions` → Developer mode → **Load unpacked** → select:

`src/ui/extension/.output/chrome-mv3`

## Reload after edit

Rebuild (`npm run build`) then click **Reload** on the extension card — no reinstall needed (pinned `manifest.key` keeps the ID stable).

Or run `npm run dev` (WXT watches and reloads).

## Firefox build (portability only — not UAT)

```bash
npm run build:firefox
```

Output lands under `.output/firefox-mv2` with WXT 0.21 (generated manifest — do not hand-edit).

## Flask

Extension `.output/` is **not** served on `:5001`. Flask only mounts `src/ui/frontend/dist`.

## Component tests (Betty)

```bash
npm run test:component
```

Looks at `tests/component/extension/` (populated after Code Complete).
