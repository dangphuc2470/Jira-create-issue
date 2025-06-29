import json
import re
import os

def update_session_from_curl():
    """
    Interactive script to update session configuration from a new curl command.
    """
    print("=== JIRA Session Updater ===")
    
    # Check if curl.txt exists and ask user preference
    if os.path.exists('curl.txt'):
        choice = input("Found curl.txt file. Use it? (y/n, default=y): ").strip().lower()
        if choice in ['', 'y', 'yes']:
            return update_session_from_file()
    
    print("Paste your new curl command below (press Enter twice when done):")
    print()
    
    # Read multi-line curl command
    curl_lines = []
    empty_line_count = 0
    
    while empty_line_count < 2:
        line = input()
        if line.strip() == "":
            empty_line_count += 1
        else:
            empty_line_count = 0
            curl_lines.append(line)
    
    curl_command = " ".join(curl_lines)
    return process_curl_command(curl_command)

def update_session_from_file():
    """
    Update session configuration from curl.txt file.
    """
    try:
        with open('curl.txt', 'r', encoding='utf-8') as f:
            curl_command = f.read().strip()
        
        print("Reading curl command from curl.txt...")
        return process_curl_command(curl_command)
        
    except FileNotFoundError:
        print("Error: curl.txt file not found.")
        return False
    except Exception as e:
        print(f"Error reading curl.txt: {e}")
        return False

def process_curl_command(curl_command):
    """
    Process curl command and update session configuration.
    """
    # Extract session data from curl command
    try:
        # Extract cookies
        cookie_match = re.search(r"-b '([^']+)'", curl_command)
        if not cookie_match:
            cookie_match = re.search(r"--header 'Cookie: ([^']+)'", curl_command)
        
        cookies = cookie_match.group(1) if cookie_match else None
        
        # Extract atl_token from cookies
        atl_token_match = re.search(r'atlassian\.xsrf\.token=([^;]+)', cookies) if cookies else None
        atl_token = atl_token_match.group(1) if atl_token_match else None
        
        # Extract form token from data
        form_token_match = re.search(r'formToken=([^&]+)', curl_command)
        form_token = form_token_match.group(1) if form_token_match else None
        
        # Extract JSESSIONID
        jsessionid_match = re.search(r'JSESSIONID=([^;]+)', cookies) if cookies else None
        jsessionid = jsessionid_match.group(1) if jsessionid_match else None
        
        # Extract URL
        url_match = re.search(r"curl '([^']+)'", curl_command)
        base_url = url_match.group(1).split('/secure/')[0] if url_match else "http://qlda.gpdn.viettel.vn"
        
        if not all([cookies, atl_token, form_token]):
            print("Error: Could not extract all required session data from curl command.")
            return False
        
        # Load existing config or create new one
        config = {}
        try:
            if os.path.exists('session_config.json') and os.path.getsize('session_config.json') > 0:
                with open('session_config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Creating new session configuration...")
        
        # Update session data
        config.update({
            'base_url': base_url,
            'cookies': cookies,
            'atl_token': atl_token,
            'form_token': form_token,
            'headers': {
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'DNT': '1',
                'Origin': base_url,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        
        # Save updated config
        with open('session_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("\n✅ Session configuration updated successfully!")
        print(f"🌐 Base URL: {base_url}")
        print(f"📄 JSESSIONID: {jsessionid}")
        print(f"🔑 ATL Token: {atl_token[:20]}...")
        print(f"📝 Form Token: {form_token[:20]}...")
        print("\nYou can now run jira.py to generate curl commands with the new session.")
        
        return True
        
    except Exception as e:
        print(f"Error processing curl command: {e}")
        return False

if __name__ == "__main__":
    update_session_from_curl()