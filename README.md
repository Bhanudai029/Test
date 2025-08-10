# 🌐 Browser Navigation Public API

**🚀 Live API:** `https://testingappbye.onrender.com`

A public API service that navigates to any URL and performs automated browser actions (ESC → TAB×7 → ENTER). Perfect for automating web navigation tasks.

## 🎯 Quick Start - Use the Public API Now!

### **For Anyone Worldwide - No Installation Required!**

#### **Option 1: One-Line Terminal Command (Linux/Mac/WSL)**
```bash
curl -s https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/public-navigate.sh | bash
```

#### **Option 2: Direct API Call**
```bash
curl -X POST https://testingappbye.onrender.com/navigate \
  -H "Content-Type: application/json" \
  -d '{"url": "facebook.com/zuck"}'
```

#### **Option 3: Use from Any Programming Language**

**Python:**
```python
import requests

response = requests.post(
    "https://testingappbye.onrender.com/navigate",
    json={"url": "facebook.com/marketplace"}
)
print(response.json())
```

**JavaScript:**
```javascript
fetch('https://testingappbye.onrender.com/navigate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({url: 'facebook.com/zuck'})
})
.then(res => res.json())
.then(data => console.log(data));
```

## Features

- 🌍 **Public API**: Available worldwide at `https://testingappbye.onrender.com`
- 🚀 **Universal**: Works with ANY website URL, not just Facebook
- 🤖 **Automated Actions**: Performs ESC → TAB×7 → ENTER sequence
- 🌐 **REST API**: Simple HTTP endpoints for browser control
- ⚡ **Fast**: Optimized headless Chrome for quick navigation
- 📋 **Returns Final URL**: Get the URL after all navigation actions

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

## 📡 Public API Endpoints

**Base URL:** `https://testingappbye.onrender.com`

### Navigate to Any URL (Main Endpoint)
```http
POST /navigate
Content-Type: application/json

{
    "url": "any-website.com/page"
}
```

**What it does:**
1. Navigates to your specified URL
2. Presses ESC (closes popups)
3. Presses TAB 7 times (navigates through elements)
4. Presses ENTER (activates element)
5. Returns the final URL after all actions

**Response:**
```json
{
    "success": true,
    "initial_url": "https://any-website.com/page",
    "final_url": "https://any-website.com/final-destination",
    "page_title": "Page Title"
}
```

### Simple GET Endpoints (For Testing)
```http
GET /api/visit/{username}
```
Example: `https://testingappbye.onrender.com/api/visit/zuck`

### Health Check
```http
GET /health
```
Returns: `{"status": "healthy"}`

### Home Page
```http
GET /
```
Returns: Interactive API documentation page

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
