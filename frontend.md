# PantryMatch 2.0 Frontend

## Overview
This is the frontend component of **PantryMatch 2.0**, providing an interactive, dynamic, and seamless web experience for smart recipe tracking, ingredient classification, and meal planning. 

## Features
- **Responsive Web Interface**: Built to operate beautifully on mobile and desktop devices.
- **Smart Ingredient Scanner**: Integrates with the backend Object Detection and ML Classifiers safely.
- **Live Recipe Search**: Communicates with the backend TF-IDF vector API to search for intelligent constraints based on user dietary and spice configurations.
- **User Authentication**: Simple session and token based profile tracking.

## Environment Variables & APIs (`apis.js`)

> [!IMPORTANT]
> **API URL Configuration**: In order for the frontend to correctly interface with the backend, you must update the global API base paths.
> Open your API configuration file (typically `apis.js` or `src/apis.js`) and modify the base URL to match your deployed URL (e.g. Vercel backend).

```javascript
// Example modification for apis.js
export const API_BASE_URL = "https://pantry-match-api.vercel.app";
```

If you are developing locally, change this back to your local Flask server port, typically `http://localhost:5000`.

## Installation & Setup

1. **Clone the repository.**
2. **Install node dependencies:**
   ```bash
   npm install
   # or yarn / pnpm
   ```
3. **Run the local development server:**
   ```bash
   npm run dev
   ```

## Deployment Notes

Deploying the frontend should ideally be completely separate from the python backend. Services like Vercel or Netlify provide seamless auto-build settings. Ensure your CI/CD pipelines track changes primarily inside the `./frontend` directory and that you correctly specify the build command (typically `npm run build`) alongside the build output directory (`dist` or `build`).
