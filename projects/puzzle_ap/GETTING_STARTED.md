# Getting Started with Sunday Night Puzzles PWA

## Quick Start

Sunday Night Puzzles PWA is now fully implemented and ready to use!

### 1. Run the Development Server

```bash
npm run dev
```

The app will open at `http://localhost:5174` (or the next available port).

### 2. Test the App

1. **Add a Puzzle**: Click the blue + button in the bottom right
2. **Upload a Photo**: Click "Upload Photo" or "Take Photo" (if on mobile)
3. **Fill in Details**: Enter puzzle name, completion date, and optional notes
4. **Save**: Your puzzle will appear in the grid view
5. **View Details**: Click on any puzzle card to see the full view
6. **Share**: Click the share button to generate a social media graphic
7. **Search**: Use the search bar to find puzzles by name or notes
8. **Edit/Delete**: Use buttons in the detail view

### 3. Test Offline Functionality

1. Open the app in your browser
2. Open Developer Tools (F12)
3. Go to the Network tab
4. Select "Offline" from the throttling dropdown
5. Refresh the page - the app should still work!
6. Add/edit/delete puzzles while offline
7. Go back online - everything persists

## Building for Production

```bash
npm run build
```

This creates an optimized build in the `dist/` directory.

## Deployment Options

### Option 1: Vercel (Recommended)

1. Install Vercel CLI: `npm install -g vercel`
2. Run: `vercel`
3. Follow the prompts
4. Your app will be live at a `.vercel.app` URL

### Option 2: Netlify

1. Go to https://app.netlify.com/
2. Drag and drop the `dist/` folder
3. Your app will be live instantly

### Option 3: GitHub Pages

1. Install gh-pages: `npm install -D gh-pages`
2. Add to package.json scripts:
   ```json
   "deploy": "npm run build && gh-pages -d dist"
   ```
3. Run: `npm run deploy`

## Replacing Placeholder Icons

The app currently uses minimal placeholder icons. Here's how to create proper ones:

### Method 1: Use the HTML Generator

1. Open `generate-icons.html` in your browser
2. Click the download buttons for each icon size
3. Save the files to `public/icons/`
4. Rebuild the app: `npm run build`

### Method 2: Use Online Tools

**Recommended Tool:** https://www.pwabuilder.com/imageGenerator

1. Upload a 512x512px source image
2. Download the generated icon package
3. Copy `icon-192x192.png`, `icon-512x512.png`, and `icon-512x512-maskable.png` to `public/icons/`
4. Rebuild the app

### Method 3: Design Your Own

Create icons with these specifications:

- **icon-192x192.png**: 192x192px, PNG, puzzle piece icon on blue background (#1976d2)
- **icon-512x512.png**: 512x512px, PNG, same design as 192x192
- **icon-512x512-maskable.png**: 512x512px, PNG, safe zone in center 80%

## Installing as a PWA

### On Mobile (Android)

1. Open the app in Chrome
2. Tap the menu (⋮) in the top right
3. Select "Add to Home Screen"
4. The app icon will appear on your home screen

### On Mobile (iOS)

1. Open the app in Safari
2. Tap the Share button
3. Select "Add to Home Screen"
4. The app icon will appear on your home screen

### On Desktop (Chrome/Edge)

1. Open the app in Chrome or Edge
2. Click the install icon (⊕) in the address bar
3. Click "Install"
4. The app will open in its own window

## Testing Checklist

Before deploying, test these features:

- [ ] Add puzzle with camera (mobile)
- [ ] Add puzzle with file upload
- [ ] View puzzle list
- [ ] Search puzzles
- [ ] View puzzle details
- [ ] Edit puzzle
- [ ] Delete puzzle
- [ ] Share puzzle (generates graphic)
- [ ] Works offline
- [ ] Installs as PWA
- [ ] Responsive on mobile
- [ ] Responsive on tablet
- [ ] Responsive on desktop

## Storage Management

The app stores all data locally using IndexedDB:

- **Average per puzzle**: ~300KB
- **Typical quota**: 50-100MB
- **Estimated capacity**: 160-320 puzzles

The app will warn you when storage reaches 80% capacity.

To check storage usage:
1. Open the app
2. The storage percentage is monitored automatically
3. You'll see a warning if it gets too high

## Troubleshooting

### Camera not working
- **Check permissions**: Make sure the browser has camera access
- **Use HTTPS**: Camera API requires HTTPS (or localhost)
- **Try file upload**: Use "Upload Photo" as a fallback

### App not installing
- **Check manifest**: Make sure icons exist in `public/icons/`
- **Use HTTPS**: PWA requires HTTPS (or localhost)
- **Check browser support**: Some older browsers don't support PWA

### Images not showing
- **Check IndexedDB**: Open DevTools > Application > IndexedDB
- **Clear cache**: Try clearing browser cache and reloading
- **Check image size**: Images over 10MB are rejected

### Offline not working
- **Check Service Worker**: DevTools > Application > Service Workers
- **Wait for registration**: Service Worker takes a few seconds to register
- **Reload twice**: First load registers SW, second load uses it

## Development Tips

### Hot Module Replacement (HMR)

Vite provides instant updates during development. Just save your file and see changes immediately.

### Debugging IndexedDB

1. Open DevTools (F12)
2. Go to Application tab
3. Click IndexedDB in the sidebar
4. Expand "puzzle-tracker-db"
5. View/edit data in the stores

### Debugging Service Worker

1. Open DevTools (F12)
2. Go to Application tab
3. Click Service Workers in the sidebar
4. View status, update, or unregister

### React DevTools

Install the React DevTools browser extension for component debugging.

## File Structure Reference

```
puzzle_ap/
├── src/
│   ├── App.jsx                 # Main app logic
│   ├── index.jsx               # Entry point
│   ├── theme.js                # UI theme
│   ├── components/             # React components
│   ├── services/               # Business logic
│   └── hooks/                  # Custom hooks
├── public/                     # Static assets
├── dist/                       # Build output (generated)
└── node_modules/              # Dependencies (generated)
```

## Environment Variables

No environment variables are needed for the basic app. If you want to add analytics or other services:

1. Create `.env` file
2. Add variables with `VITE_` prefix:
   ```
   VITE_API_URL=https://api.example.com
   ```
3. Access in code: `import.meta.env.VITE_API_URL`

## Google Play Store Deployment

To deploy to Google Play Store:

1. **Deploy PWA to HTTPS domain first**
2. **Install Bubblewrap**:
   ```bash
   npm install -g @bubblewrap/cli
   ```
3. **Initialize TWA**:
   ```bash
   bubblewrap init --manifest https://your-domain.com/manifest.webmanifest
   ```
4. **Build Android package**:
   ```bash
   bubblewrap build
   ```
5. **Create Play Store listing**:
   - Screenshots (2-8 images)
   - Feature graphic (1024x500)
   - App description
   - Privacy policy URL
6. **Upload APK/AAB** to Play Console
7. **Submit for review**

## Support & Resources

- **Issues**: Check the browser console for errors
- **PWA Testing**: Use Lighthouse in Chrome DevTools
- **Icon Generator**: https://www.pwabuilder.com/imageGenerator
- **TWA Setup**: https://github.com/GoogleChromeLabs/bubblewrap
- **Material-UI Docs**: https://mui.com/
- **Vite Docs**: https://vitejs.dev/

## What's Next?

Now that the app is working, consider:

1. **Replace icons** with proper branded icons
2. **Test on real devices** (iOS, Android)
3. **Deploy to production** hosting
4. **Get user feedback** before Play Store submission
5. **Add analytics** (optional)
6. **Implement cloud sync** (future enhancement)
7. **Add dark mode** (future enhancement)

---

**You're ready to go! Run `npm run dev` and start tracking puzzles!** 🧩
