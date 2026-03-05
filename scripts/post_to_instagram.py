import os
import json
import requests
from datetime import datetime
import sys

INSTAGRAM_ACCESS_TOKEN = os.environ['INSTAGRAM_ACCESS_TOKEN']
INSTAGRAM_ACCOUNT_ID = os.environ['INSTAGRAM_ACCOUNT_ID']
GRAPH_API_VERSION = "v19.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


def get_next_post(queue_file="content/queue.json"):
    with open(queue_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    today = datetime.now().strftime("%Y-%m-%d")
    for post in data['posts']:
        if not post['posted'] and post['scheduled_date'] <= today:
            return post, data
    return None, data


def create_media_container(image_url, caption):
    url = f"{BASE_URL}/{INSTAGRAM_ACCOUNT_ID}/media"
    params = {
        'image_url': image_url,
        'caption': caption,
        'access_token': INSTAGRAM_ACCESS_TOKEN
    }
    response = requests.post(url, params=params)
    if not response.ok:
        print(f"Errore creazione container: {response.text}")
        response.raise_for_status()
    return response.json()['id']


def publish_media(container_id):
    url = f"{BASE_URL}/{INSTAGRAM_ACCOUNT_ID}/media_publish"
    params = {
        'creation_id': container_id,
        'access_token': INSTAGRAM_ACCESS_TOKEN
    }
    response = requests.post(url, params=params)
    if not response.ok:
        print(f"Errore pubblicazione: {response.text}")
        response.raise_for_status()
    return response.json()['id']


def mark_as_posted(data, post_id, queue_file="content/queue.json"):
    for post in data['posts']:
        if post['id'] == post_id:
            post['posted'] = True
            post['posted_at'] = datetime.now().isoformat()
            break
    with open(queue_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def debug_token():
    print("=== DEBUG TOKEN ===")
    r = requests.get(f"{BASE_URL}/me", params={'access_token': INSTAGRAM_ACCESS_TOKEN, 'fields': 'id,name'})
    print(f"Token identity: {r.json()}")

    r2 = requests.get(f"{BASE_URL}/me/accounts", params={'access_token': INSTAGRAM_ACCESS_TOKEN, 'fields': 'id,name,instagram_business_account'})
    print(f"Pages accessibili: {r2.json()}")

    r3 = requests.get(f"{BASE_URL}/{INSTAGRAM_ACCOUNT_ID}", params={'access_token': INSTAGRAM_ACCESS_TOKEN, 'fields': 'id,name,username'})
    print(f"IG Account {INSTAGRAM_ACCOUNT_ID}: {r3.json()}")
    print("=== FINE DEBUG ===")


def main():
    debug_token()
    post, data = get_next_post()
    if not post:
        print("Nessun post da pubblicare oggi.")
        sys.exit(0)

    print(f"Pubblicando post ID {post['id']}: {post['caption'][:60]}...")

    container_id = create_media_container(post['image_url'], post['caption'])
    print(f"Container creato: {container_id}")

    media_id = publish_media(container_id)
    print(f"Post pubblicato! Media ID: {media_id}")

    mark_as_posted(data, post['id'])
    print("Queue aggiornata.")


if __name__ == "__main__":
    main()
