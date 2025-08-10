# Lightweight Facebook Browser API

A lightweight headless browser service optimized for Facebook navigation, deployable on Render.com.

## Features

- 🚀 **Lightweight**: Minimal resource usage with optimized Chrome settings
- 🤖 **Automated Actions**: Performs predefined key sequences (Escape, 7x Tab, Enter)
- 🌐 **REST API**: Simple HTTP endpoints for browser control
- ☁️ **Cloud Ready**: Configured for Render.com deployment
- 🔄 **Singleton Pattern**: Reuses browser instance for efficiency

## Local Testing

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Flask app:
```bash
python app.py
```

3. Test the API:
```bash
curl -X POST http://localhost:10000/navigate \
  -H "Content-Type: application/json" \
  -d '{"url": "facebook.com/marketplace"}'
```

## Deploy to Render.com

### Method 1: Using render.yaml (Recommended)

1. Push your code to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

2. Connect to Render:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`
   - Click "Apply" to deploy

### Method 2: Using Dockerfile

1. In Render Dashboard:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Choose "Docker" as the environment
   - Set build and deploy settings
   - Click "Create Web Service"

## API Endpoints

### Home Page
```
GET /
```
Returns HTML page with API documentation

### Health Check
```
GET /health
```
Returns service health status

### Navigate to URL
```
POST /navigate
Content-Type: application/json

{
    "url": "facebook.com/marketplace"
}
```

Response:
```json
{
    "success": true,
    "initial_url": "https://www.facebook.com/marketplace",
    "final_url": "https://www.facebook.com/...",
    "page_title": "Facebook - Marketplace"
}
```

### Shutdown Browser
```
POST /shutdown
```
Gracefully closes the browser instance

## Optimization Tips

1. **Free Tier Limits**: Render's free tier has memory limits. This app is optimized to run within 512MB RAM.

2. **Cold Starts**: The first request may be slower as it initializes the browser. Subsequent requests reuse the instance.

3. **Timeout**: Requests have a 120-second timeout to accommodate page loading and actions.

## Environment Variables

Set these in Render's environment settings if needed:

- `PORT`: Port number (default: 10000)
- `PYTHONUNBUFFERED`: Set to "1" for real-time logs
- `WDM_LOCAL`: Set to "1" to use local ChromeDriver

## Troubleshooting

- **Browser won't start**: Check Chrome installation in logs
- **Out of memory**: Reduce worker count or use smaller window size
- **Timeout errors**: Increase timeout in gunicorn settings

## Files Structure

```
victory/
├── app.py                 # Flask API server
├── headless_browser.py    # Original browser script
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment config
├── Dockerfile            # Docker deployment option
├── .gitignore           # Git ignore file
└── README.md            # This file
```

## License

MIT License - Feel free to modify and deploy!
