# Datacuse MCP site

A dependency-free static landing page for Datacuse MCP.

## Run locally

Requires Node.js 18 or newer. No package installation is needed.

```powershell
node server.mjs
```

Then open <http://localhost:4173>. You can also use `npm start`. To choose another port, run `node server.mjs 8080`.

## Deploy

This directory is already included in the repository's GitHub Pages deployment. It can also be uploaded directly to Netlify, Cloudflare Pages, S3, or any ordinary static web server. There is no build command and the publish directory is this folder.
