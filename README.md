# Taiga Migration

This is a migration script to copy issues from a Google Doc into Taiga.

## Requirements
To run this script, ensure you have **Python 3** installed on your system. You will also need the `beautifulsoup4` and `requests` packages. You can install them by running:
```bash
pip install beautifulsoup4 requests
```

## File Structure
Ensure your files are placed in the following directory layout for the script to correctly pick up the HTML file and its associated images:

```text
- migrate_to_taiga.py
- <htmlfile_name>.html
- images/
  -- img.png
  -- img2.png
```

## Use Case
1. Convert that Word document to HTML.
2. Select all tabs to ensure all data is exported.
3. Place the HTML file in the same directory as the script.

The script will automatically parse the predefined tabs from the generated HTML and create user stories in Taiga, complete with descriptions, images, and video links found in the doc.

## Configuration & Setup
Before running the script, you must provide your Taiga credentials and project settings within the script `migrate_to_taiga.py`:

```python
TAIGA_URL = "".rstrip("/")
USERNAME = ""
PASSWORD = ""
PROJECT_ID = 00
```

**Note on Credentials:** You must provide a valid `USERNAME` and `PASSWORD`. If your password is not available, you can use the "Forgot Password" feature on the Taiga login screen to generate a new one.

## Running the Migration
Once the configuration is updated and the HTML file is present, simply run:

```bash
python3 migrate_to_taiga.py
```
