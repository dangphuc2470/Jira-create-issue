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
        base_url = url_match.group(1) if url_match else "http://qlda.gpdn.viettel.vn/secure/QuickCreateIssue.jspa?decorator=none"
        
        # Extract data payload and convert to template
        data_match = re.search(r"--data-raw '([^']+)'", curl_command)
        data_payload = data_match.group(1) if data_match else None
        
        if not all([cookies, atl_token, form_token, data_payload]):
            print("Error: Could not extract all required session data from curl command.")
            print(f"Cookies: {'✓' if cookies else '✗'}")
            print(f"ATL Token: {'✓' if atl_token else '✗'}")
            print(f"Form Token: {'✓' if form_token else '✗'}")
            print(f"Data Payload: {'✓' if data_payload else '✗'}")
            return False
        
        # Convert data payload to template with placeholders
        data_template = data_payload
        
        # Replace specific summary with placeholder
        summary_match = re.search(r'summary=([^&]+)', data_template)
        if summary_match:
            data_template = data_template.replace(f'summary={summary_match.group(1)}', 'summary={SUMMARY}')
        
        # Replace specific dates with placeholders
        # Find and replace start date (customfield_10519)
        start_date_match = re.search(r'customfield_10519=([^&]+)', data_template)
        if start_date_match:
            data_template = data_template.replace(f'customfield_10519={start_date_match.group(1)}', 'customfield_10519={START_DATE}')
        
        # Find and replace due date
        due_date_match = re.search(r'duedate=([^&]+)', data_template)
        if due_date_match:
            data_template = data_template.replace(f'duedate={due_date_match.group(1)}', 'duedate={END_DATE}')
        
        # Find and replace actual date (customfield_10603)
        actual_date_match = re.search(r'customfield_10603=([^&]+)', data_template)
        if actual_date_match:
            data_template = data_template.replace(f'customfield_10603={actual_date_match.group(1)}', 'customfield_10603={ACTUAL_DATE}')
        
        # Replace tokens with placeholders
        data_template = data_template.replace(f'atl_token={atl_token}', 'atl_token={ATL_TOKEN}')
        data_template = data_template.replace(f'formToken={form_token}', 'formToken={FORM_TOKEN}')
        
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
            'data_payload_template': data_template,
            'headers': {
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'DNT': '1',
                'Origin': base_url.split('/secure')[0] if '/secure' in base_url else base_url,
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
        print(f"📦 Data Template: {data_template[:100]}...")
        print("\nYou can now run jira.py to generate curl commands with the new session.")
        
        return True
        
    except Exception as e:
        print(f"Error processing curl command: {e}")
        return False

if __name__ == "__main__":
    update_session_from_curl()