import requests
from bs4 import BeautifulSoup
import json
import smtplib
from email.mime.text import MIMEText
import os

URL = "https://iiis.tsinghua.edu.cn/seminars/"
DATA_FILE = "seminars.json"

def fetch_seminars():
    response = requests.get(URL)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    seminars = []
    rows = soup.select('tbody tr')

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

def load_old_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def send_email(new_items):
    sender = os.environ["EMAIL_SENDER"]
    password = os.environ["EMAIL_PASSWORD"]
    receiver = os.environ["EMAIL_RECEIVER"]

    content = "New seminars found:\n\n"
    for item in new_items:
        content += f"{item['number']} - {item['title']}\n{item['link']}\n\n"

    msg = MIMEText(content)
    msg['Subject'] = 'New IIIS Seminars Detected'
    msg['From'] = sender
    msg['To'] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())

def main():
    new_data = fetch_seminars()
    old_data = load_old_data()
    old_numbers = {s['number'] for s in old_data}
    new_items = [s for s in new_data if s['number'] not in old_numbers]

    if new_items:
        print(f"Found {len(new_items)} new seminars.")
        send_email(new_items)
        save_data(new_data)
    else:
        print("No new seminars.")

if __name__ == "__main__":
    main()
