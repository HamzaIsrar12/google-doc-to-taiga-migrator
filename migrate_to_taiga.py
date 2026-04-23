import os
import requests
from bs4 import BeautifulSoup

# =========================
# CONFIG
# =========================

TAIGA_URL = "".rstrip("/")
USERNAME = ""
PASSWORD = ""
PROJECT_ID = 0
HTML_FILE = None  # auto-detect if None

# =========================
# AUTH
# =========================

def get_auth_token():
    url = f"{TAIGA_URL}/api/v1/auth"

    payload = {
        "type": "normal",
        "username": USERNAME,
        "password": PASSWORD
    }

    r = requests.post(url, json=payload)

    print("AUTH STATUS:", r.status_code)
    print("AUTH RESPONSE:", r.text)

    r.raise_for_status()

    return r.json()["auth_token"]


# =========================
# CREATE USER STORY
# =========================

def create_user_story(token, subject, description):

    url = f"{TAIGA_URL}/api/v1/userstories"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "project": PROJECT_ID,
        "subject": subject[:500],
        "description": description
    }

    r = requests.post(url, json=payload, headers=headers)

    print("\nCREATE STATUS:", r.status_code)
    print("CREATE RESPONSE:", r.text)

    if r.status_code == 403:
        raise Exception("403 Forbidden: Check PROJECT_ID, permissions, or token scope")

    r.raise_for_status()

    return r.json()["id"]


# =========================
# UPLOAD IMAGE
# =========================

def upload_attachment(token, story_id, filepath):

    url = f"{TAIGA_URL}/api/v1/userstories/attachments"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    with open(filepath, "rb") as f:
        files = {"attached_file": f}

        data = {
            "project": PROJECT_ID,
            "object_id": story_id
        }

        r = requests.post(url, headers=headers, files=files, data=data)

    print("UPLOAD:", filepath, r.status_code)

    r.raise_for_status()


# =========================
# FIND HTML FILE
# =========================

def find_html():
    if HTML_FILE:
        return HTML_FILE

    for f in os.listdir("."):
        if f.endswith(".html"):
            return f

    raise Exception("No HTML file found in directory")


# =========================
# PARSE HTML
# =========================

def parse_html(html_file):

    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    stories = []

    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        if not rows:
            continue

        headers = [h.get_text(strip=True) for h in rows[0].find_all(["td", "th"])]

        for row in rows[1:]:

            cells = row.find_all("td")
            values = [c.get_text(strip=True) for c in cells]

            row_data = dict(zip(headers, values))

            dev_comments = row_data.get("Dev Team Comments", "").lower()

            # Skip already migrated
            if "taiga" in dev_comments:
                print("SKIP:", row_data.get("Description", "")[:60])
                continue

            subject = row_data.get("Description", "Untitled Issue")

            # Build description, only including non-empty sections
            description_parts = []
            
            # Add Description only if not empty
            description_text = row_data.get("Description", "").strip()
            if description_text:
                description_parts.append(f"Description:\n{description_text}")
            
            # Add Comments only if not empty
            comments_text = row_data.get("Comments", "").strip()
            if comments_text:
                description_parts.append(f"Comments:\n{comments_text}")
            
            # Extract all video URLs (multiple possible)
            video_urls = []
            for link in row.find_all("a"):
                href = link.get("href", "")
                link_text = link.get_text(strip=True)
                if href and ("mp4" in link_text.lower() or "video" in link_text.lower()):
                    video_urls.append(f"{link_text}: {href}")
            
            if video_urls:
                description_parts.append(f"Videos:\n" + "\n".join(video_urls))
            
            # Add Priority only if not empty
            priority_text = row_data.get("Priority", "").strip()
            if priority_text:
                description_parts.append(f"Priority:\n{priority_text}")
            
            description = "\n\n".join(description_parts) if description_parts else "(No description provided)"

            # Extract all images (multiple possible)
            images = []
            for img in row.find_all("img"):
                src = img.get("src")
                if src and os.path.exists(src):
                    images.append(src)

            stories.append({
                "subject": subject,
                "description": description,
                "images": images,
                "videos": video_urls
            })

    return stories


# =========================
# MAIN
# =========================

def main():

    html_file = find_html()

    print("Using HTML:", html_file)

    stories = parse_html(html_file)

    print("Total stories to create:", len(stories))

    token = get_auth_token()

    for i, s in enumerate(stories, 1):

        print(f"\n[{i}/{len(stories)}] Creating:", s["subject"][:80])
        
        # Log video information if present
        if s.get("videos"):
            print(f"  → Videos found: {len(s['videos'])}")
            for vid in s['videos']:
                print(f"    {vid[:100]}...")
        
        # Log image information
        if s["images"]:
            print(f"  → Images found: {len(s['images'])}")

        try:
            story_id = create_user_story(
                token,
                s["subject"],
                s["description"]
            )

            for img in s["images"]:
                upload_attachment(token, story_id, img)

        except Exception as e:
            print("FAILED STORY:", s["subject"])
            print("ERROR:", str(e))
            continue

    print("\nMIGRATION COMPLETE")


if __name__ == "__main__":
    main()
