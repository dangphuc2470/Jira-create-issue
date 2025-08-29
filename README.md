## Jira Create Issue - Excel to cURL

Generate Jira QuickCreateIssue cURL commands from an Excel sheet, using your current browser session copied from a working cURL.

### Prerequisites
- Python 3.8+
- Have a working Jira Quick Create curl captured from your browser (e.g., via DevTools > Copy as cURL) and paste it into `curl.txt`.

### Install
```bash
pip install -r requirements.txt
```

### Prepare Input
1. Open `input_data.xlsx` → sheet `Sheet1`.
2. Fill rows with:
   - Column A: Start Date (DD/MM/YYYY)
   - Column B: End Date (DD/MM/YYYY) — script will change to end-of-month automatically
   - Column C: Task name (summary)
3. Save and close the Excel file.

### Update Session From Your cURL
Put your latest successful Jira QuickCreate cURL into `curl.txt` (single command).

Then run:
```bash
python update_session.py
```
This extracts cookies, tokens, and builds a data template in `session_config.json`.

### Optional: Remove [Mobile] Prefix
By default, summaries are prefixed with `[Mobile]` in `jira.py`.
To remove, delete or comment the line in `jira.py`:
```python
summary = f"[Mobile] {summary}"
```

### Generate cURL Commands
```bash
python jira.py
```
This writes a full multi-line cURL per row to column E of `input_data.xlsx`.

Behavior:
- End date is adjusted to the end of its month automatically.
- `timetracking_originalestimate` and `timetracking_remainingestimate` are calculated as the day difference between Start Date and Actual Date (Actual Date = End Date).
- Dates are formatted as d/MM/yy and URL-encoded in the payload.

### Execute the cURLs
Open `input_data.xlsx`, copy each generated cURL from column E, and run it in your terminal to create issues.

### Notes
- If Jira rejects dates, verify they appear like `2/06/25` (day without leading zero) in the encoded payload.
- If your session expires, update `curl.txt` with a fresh cURL and run `python update_session.py` again.

