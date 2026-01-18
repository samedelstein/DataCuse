# App Icons

This directory should contain the following icon files:

- `icon-192x192.png` - 192x192px app icon
- `icon-512x512.png` - 512x512px app icon
- `icon-512x512-maskable.png` - 512x512px maskable icon (with safe zone)

## Generating Icons

You can use the following tools to generate icons from a source image:

1. **PWA Asset Generator**: https://github.com/elegantapp/pwa-asset-generator
   ```bash
   npx pwa-asset-generator source-icon.png ./public/icons
   ```

2. **RealFaviconGenerator**: https://realfavicongenerator.net/

3. **Maskable.app**: https://maskable.app/editor (for maskable icons)

## Design Guidelines

- Use a simple, recognizable puzzle piece icon
- Primary color: #1976d2 (Material-UI blue)
- Background: White or transparent
- Maskable icons should have content within the safe zone (center 80%)

## Placeholder Icons

For development, you can use placeholder icons from https://placeholder.com/ or create simple colored squares.

Example placeholder creation (using ImageMagick):
```bash
convert -size 192x192 xc:#1976d2 -gravity center -pointsize 48 -fill white -annotate +0+0 "PT" icon-192x192.png
convert -size 512x512 xc:#1976d2 -gravity center -pointsize 128 -fill white -annotate +0+0 "PT" icon-512x512.png
convert -size 512x512 xc:#1976d2 -gravity center -pointsize 128 -fill white -annotate +0+0 "PT" icon-512x512-maskable.png
```
