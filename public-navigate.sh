#!/bin/bash
# Universal Browser Navigation Tool - Works on any system with curl
# This script can be run from anywhere to use the public API

# Color codes for pretty output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Public API endpoint
API_URL="https://testingappbye.onrender.com"

# Function to display banner
show_banner() {
    clear
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║         🌐 BROWSER NAVIGATION PUBLIC API 🌐                 ║"
    echo "║                                                              ║"
    echo "║  Navigate to any URL with automated actions:                ║"
    echo "║  ESC → TAB×7 → ENTER                                        ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Function to check API health
check_api() {
    echo -e "${YELLOW}🔍 Checking API status...${NC}"
    
    # Check if API is healthy
    response=$(curl -s -w "\n%{http_code}" "${API_URL}/health" 2>/dev/null)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" == "200" ]; then
        echo -e "${GREEN}✅ API is online and ready!${NC}"
        echo -e "${CYAN}Server: ${API_URL}${NC}"
        return 0
    else
        echo -e "${RED}❌ API is not responding. It might be starting up...${NC}"
        echo -e "${YELLOW}Please wait 30 seconds and try again.${NC}"
        echo -e "${YELLOW}Or check status at: ${API_URL}${NC}"
        return 1
    fi
}

# Function to navigate to URL
navigate_url() {
    local url="$1"
    
    echo -e "\n${CYAN}📍 Target URL: ${url}${NC}"
    echo -e "${YELLOW}🚀 Starting navigation...${NC}\n"
    
    # Start timer
    start_time=$(date +%s)
    
    # Show progress indicator
    echo -ne "${YELLOW}   ⏳ Navigating"
    
    # Make API request
    response=$(curl -s -X POST "${API_URL}/navigate" \
        -H "Content-Type: application/json" \
        -d "{\"url\": \"${url}\"}" \
        2>/dev/null &)
    
    # Get the PID of the curl command
    curl_pid=$!
    
    # Show animated progress while waiting
    spin='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    i=0
    elapsed=0
    while kill -0 $curl_pid 2>/dev/null; do
        i=$(( (i+1) %10 ))
        elapsed=$(( $(date +%s) - start_time ))
        echo -ne "\r${YELLOW}   ⏳ Navigating... (${elapsed}s) ${spin:$i:1}  ${NC}"
        sleep 0.1
    done
    
    # Wait for curl to finish and get response
    wait $curl_pid
    response=$(curl -s -X POST "${API_URL}/navigate" \
        -H "Content-Type: application/json" \
        -d "{\"url\": \"${url}\"}" \
        2>/dev/null)
    
    # Calculate total time
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    # Clear the progress line
    echo -ne "\r                                                  \r"
    
    # Parse response
    if echo "$response" | grep -q '"success":true'; then
        echo -e "${GREEN}✅ Navigation successful! (Time: ${duration}s)${NC}\n"
        
        # Extract URLs from JSON response
        initial_url=$(echo "$response" | grep -o '"initial_url":"[^"]*' | cut -d'"' -f4)
        final_url=$(echo "$response" | grep -o '"final_url":"[^"]*' | cut -d'"' -f4)
        page_title=$(echo "$response" | grep -o '"page_title":"[^"]*' | cut -d'"' -f4)
        
        echo -e "${CYAN}📊 Results:${NC}"
        echo -e "${BLUE}─────────────────────────────────────────────────${NC}"
        echo -e "${YELLOW}  🔗 Initial URL: ${NC}${initial_url}"
        echo -e "${GREEN}  🎯 Final URL:   ${NC}${CYAN}${final_url}${NC}"
        
        if [ ! -z "$page_title" ]; then
            echo -e "${YELLOW}  📄 Page Title:  ${NC}${page_title}"
        fi
        
        # Check if it's a photo URL
        if [[ "$final_url" == *"photo"* ]] && [[ "$final_url" == *"fbid"* ]]; then
            echo -e "\n${MAGENTA}  📸 Photo URL detected!${NC}"
        fi
        
        echo -e "${BLUE}─────────────────────────────────────────────────${NC}"
        
        # Try to copy to clipboard (if available)
        if command -v pbcopy &> /dev/null; then
            echo "$final_url" | pbcopy
            echo -e "\n${GREEN}📋 Final URL copied to clipboard! (macOS)${NC}"
        elif command -v xclip &> /dev/null; then
            echo "$final_url" | xclip -selection clipboard
            echo -e "\n${GREEN}📋 Final URL copied to clipboard! (Linux)${NC}"
        elif command -v clip &> /dev/null; then
            echo "$final_url" | clip
            echo -e "\n${GREEN}📋 Final URL copied to clipboard! (Windows)${NC}"
        fi
        
        return 0
    else
        echo -e "${RED}❌ Navigation failed! (Time: ${duration}s)${NC}"
        
        # Try to extract error message
        error=$(echo "$response" | grep -o '"error":"[^"]*' | cut -d'"' -f4)
        if [ ! -z "$error" ]; then
            echo -e "${RED}   Error: ${error}${NC}"
        else
            echo -e "${RED}   Error: Unable to navigate to URL${NC}"
        fi
        
        return 1
    fi
}

# Main execution
show_banner

# Check if API is available
if ! check_api; then
    exit 1
fi

echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"

# Main loop
while true; do
    # Get URL input
    echo -e "${YELLOW}Enter URL to navigate to:${NC}"
    echo -e "${CYAN}Examples:${NC}"
    echo -e "  • facebook.com/zuck"
    echo -e "  • facebook.com/marketplace"
    echo -e "  • https://www.example.com"
    echo -e "  • any-website.com/page"
    echo -e "\nType 'exit' to quit"
    echo -e ""
    echo -ne "${CYAN}URL: ${NC}"
    read -r url_input
    
    # Check for exit
    if [ "$url_input" == "exit" ] || [ "$url_input" == "quit" ] || [ "$url_input" == "q" ]; then
        echo -e "\n${YELLOW}👋 Goodbye!${NC}\n"
        break
    fi
    
    # Check for empty input
    if [ -z "$url_input" ]; then
        echo -e "${RED}❌ URL cannot be empty!${NC}\n"
        continue
    fi
    
    # Navigate to the URL
    navigate_url "$url_input"
    
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"
    
    # Ask if user wants to continue
    echo -ne "${YELLOW}Press Enter to navigate to another URL, or type 'exit' to quit: ${NC}"
    read -r continue_input
    
    if [ "$continue_input" == "exit" ] || [ "$continue_input" == "quit" ] || [ "$continue_input" == "q" ]; then
        echo -e "\n${YELLOW}👋 Goodbye!${NC}\n"
        break
    fi
    
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"
done

echo -e "${GREEN}✨ Thank you for using the Browser Navigation API!${NC}\n"
