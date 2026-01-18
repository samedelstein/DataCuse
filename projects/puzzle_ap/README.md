# Puzzle Tracker PWA

A Progressive Web App for tracking completed jigsaw puzzles with offline support, camera integration, and social media sharing capabilities.

## Features

- **Photo Capture**: Use your device camera or upload photos of completed puzzles
- **Offline Support**: Works completely offline with IndexedDB storage
- **Share Puzzles**: Generate beautiful share graphics for social media
- **Search & Filter**: Quickly find puzzles by name or notes
- **Mobile-First**: Optimized for mobile devices with touch gestures
- **PWA**: Installable on any device (iOS, Android, Desktop)

## Tech Stack

- React 18
- Material-UI v5
- IndexedDB (with idb wrapper)
- Vite with PWA plugin
- Workbox (Service Worker)

## Getting Started

### Prerequisites

- Node.js 16+ and npm

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Development

The app will be available at `http://localhost:5173` when running the development server.

### Project Structure

```
puzzle_ap/
├── public/
│   ├── icons/          # App icons for PWA
│   └── manifest.json   # PWA manifest
├── src/
│   ├── components/     # React components
│   ├── services/       # Business logic (DB, images, sharing)
│   ├── hooks/          # Custom React hooks
│   ├── theme.js        # Material-UI theme
│   ├── App.jsx         # Main app component
│   └── index.jsx       # Entry point
└── vite.config.js      # Vite configuration
```

## Building for Production

```bash
npm run build
```

The production build will be in the `dist` directory, ready for deployment.

## Deployment

### Web Deployment

Deploy the `dist` folder to any static hosting service:

- **Vercel**: Connect your GitHub repo and deploy automatically
- **Netlify**: Drag and drop the `dist` folder or connect via GitHub
- **GitHub Pages**: Use the `gh-pages` branch

### Google Play Store (TWA)

1. Deploy the PWA to a custom domain with HTTPS
2. Use [Bubblewrap](https://github.com/GoogleChromeLabs/bubblewrap) to generate an Android app:
   ```bash
   npx @bubblewrap/cli init --manifest https://your-domain.com/manifest.json
   npx @bubblewrap/cli build
   ```
3. Submit the generated APK/AAB to Google Play Store

## Storage

The app uses IndexedDB for storing:
- Puzzle metadata (name, date, notes)
- Compressed images (max 1024px, JPEG)
- Thumbnails (max 256px, JPEG)

Estimated storage per puzzle: ~300KB

## Browser Support

- Chrome/Edge (Android + Desktop) ✓
- Safari (iOS 16.4+) ✓
- Firefox (Android + Desktop) ✓
- Samsung Internet ✓

## License

MIT

## Contributing

Pull requests are welcome! For major changes, please open an issue first.
