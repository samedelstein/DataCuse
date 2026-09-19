# Repository Guidelines

## Project Structure & Module Organization

This repository hosts the public DataCuse website and standalone Syracuse-focused projects. The root `index.html` is the main landing page, `public/` contains shared screenshots and static assets, and `projects/` contains project pages and apps. Built static projects such as `projects/ocpl-library-story/` and `projects/below-the-line/` are committed as deployable HTML/assets. Active Vite apps live in `projects/cityline-bypass/` and `projects/puzzle_ap/`, with source under each app's `src/` directory.

## Build, Test, and Development Commands

There is no root package script; run commands from the app directory you are changing.

```bash
cd projects/cityline-bypass
npm ci
npm run dev      # start Vite locally
npm run build    # create dist/ for GitHub Pages
npm run lint     # run ESLint
```

```bash
cd projects/puzzle_ap
npm ci
npm run dev
npm run build
npm run lint
```

The GitHub Pages workflow in `.github/workflows/pages-projects.yml` builds both Vite apps with Node 20 and copies their `dist/` output into the deployed site.

## Coding Style & Naming Conventions

Use JavaScript/JSX modules and follow the style already present in each subproject. Prefer 2-space indentation in JSX/CSS, PascalCase for React components (`PuzzleDetail.jsx`), camelCase for hooks and services (`useIndexedDB.js`, `imageService.js`), and descriptive kebab-case for static project directories (`cityline-bypass`). Keep static asset names lowercase with underscores or hyphens.

Run the local lint command before committing app changes. `cityline-bypass` uses ESLint 9 flat config with React Hooks and React Refresh rules; `puzzle_ap` uses ESLint 8 over `src`.

## Testing Guidelines

No formal test suite is currently wired into package scripts. For now, verify changes with `npm run lint`, `npm run build`, and a local browser check via `npm run dev` or `npm run preview`. If adding tests, prefer colocated `*.test.jsx` files and add a package `test` script so future contributors can run them consistently.

## Commit & Pull Request Guidelines

Recent commits use concise, imperative messages such as `Host Syracuse performance dashboard` and `Refresh OCPL story design`. Keep commits focused on one project or site update. Pull requests should describe the user-facing change, list affected paths, note build/lint results, link any related issue, and include screenshots for visual changes.

## Security & Configuration Tips

Do not commit secrets or local `.env` files. `cityline-bypass` may use `VITE_GEMINI_API_KEY` during the Pages build; configure it through GitHub Actions secrets or local environment variables.
