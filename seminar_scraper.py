import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://iiis.tsinghua.edu.cn/seminars/"
DATA_FILE = "seminars.json"

def fetch_seminars():
    response = requests.get(URL)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    seminars = []
    rows = soup.select('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 5:
            continue
        number = cols[0].text.strip()
        title = cols[1].get_text(strip=True)
        link = cols[1].find('a')['href']
        speaker_info = cols[2].get_text(strip=True)
        time = cols[3].text.strip()
        location = cols[4].text.strip()
        seminars.append({
            "number": number,
            "title": title,
            "link": f"https://iiis.tsinghua.edu.cn{link}",
            "speaker_info": speaker_info,
            "time": time,
            "location": location
        })
    return seminars

def load_old():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_new(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def detect_changes(new, old):
    old_numbers = {x['number'] for x in old}
    return [x for x in new if x['number'] not in old_numbers]

if __name__ == "__main__":
    new_data = fetch_seminars()
    old_data = load_old()
    changes = detect_changes(new_data, old_data)
    if changes:
        print("🔔 New seminars found:")
        for item in changes:
            print(f"- [{item['number']}] {item['title']} ({item['speaker_info']})")
    else:
        print("✅ No new seminars.")
    save_new(new_data)
