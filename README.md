# Reelify - Topic to MP3/Video Generator

A static website for generating videos, images, and captions from text prompts, optimized for GitHub Pages deployment.

## Overview

Reelify is a web application that allows users to:

1. Generate videos from text topics
2. Create images from text prompts
3. Add captions to videos

This version is a static site that can be deployed on GitHub Pages. It simulates the API functionality with client-side JavaScript.

## GitHub Pages Deployment

### Automatic Deployment

1. Fork this repository
2. Go to your repository settings
3. Navigate to "Pages" in the sidebar
4. Under "Source", select "Deploy from a branch"
5. Select the "main" branch and "/ (root)" folder
6. Click "Save"
7. Your site will be deployed at `https://your-username.github.io/topic-to-mp3/`

### Manual Deployment

If you prefer to deploy manually:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/topic-to-mp3.git
   cd topic-to-mp3
   ```

2. Make any desired changes

3. Commit and push to the main branch:
   ```bash
   git add .
   git commit -m "Update site"
   git push origin main
   ```

4. GitHub will automatically deploy your changes

## Project Structure

```
├── index.html              # Home page
├── video-generator.html    # Video generator page
├── image-generator.html    # Image generator page
├── captioner.html          # Captioner page
├── css/                    # CSS styles
│   └── styles.css          # Main stylesheet
├── js/                     # JavaScript files
│   └── scripts.js          # Client-side functionality
└── README.md               # Project documentation
```

## Local Development

To run the site locally:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/topic-to-mp3.git
   cd topic-to-mp3
   ```

2. Open the site in a web browser:
   - You can simply open `index.html` in your browser
   - Or use a local server:
     ```bash
     # Using Python
     python -m http.server
     
     # Using Node.js
     npx serve
     ```

3. The site will be available at `http://localhost:8000` (or similar port)

## Customization

- Edit HTML files to change the UI
- Modify `css/styles.css` to customize the appearance
- Update `js/scripts.js` to change the client-side functionality

## Converting to a Full Application

This static site simulates API functionality with client-side JavaScript. To convert it to a full application:

1. Create a backend API with Flask, Express, or another framework
2. Update the JavaScript fetch calls to point to your real API endpoints
3. Deploy the backend to a server or serverless platform

## License

MIT 