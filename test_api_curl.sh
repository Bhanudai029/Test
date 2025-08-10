#!/bin/bash

# Facebook Browser API Test Commands
# API URL: https://testingappbye.onrender.com

echo "=========================================="
echo "Facebook Browser API - cURL Test Examples"
echo "=========================================="

# 1. Health Check
echo ""
echo "1. Testing Health Check:"
echo "------------------------"
curl -X GET https://testingappbye.onrender.com/health

# 2. Navigate to your requested URL
echo ""
echo ""
echo "2. Navigate to https://www.facebook.com/abestoflife:"
echo "----------------------------------------------------"
curl -X POST https://testingappbye.onrender.com/navigate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.facebook.com/abestoflife"}'

# 3. Navigate to Facebook Marketplace
echo ""
echo ""
echo "3. Navigate to Facebook Marketplace:"
echo "------------------------------------"
curl -X POST https://testingappbye.onrender.com/navigate \
  -H "Content-Type: application/json" \
  -d '{"url": "facebook.com/marketplace"}'

# 4. Navigate using short URL
echo ""
echo ""
echo "4. Navigate to Mark Zuckerberg's profile (short URL):"
echo "-----------------------------------------------------"
curl -X POST https://testingappbye.onrender.com/navigate \
  -H "Content-Type: application/json" \
  -d '{"url": "zuck"}'

echo ""
echo ""
echo "=========================================="
echo "All tests completed!"
echo "=========================================="
