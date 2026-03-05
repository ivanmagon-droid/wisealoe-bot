import os
import json
import requests
from datetime import datetime
import sys

INSTAGRAM_ACCESS_TOKEN = os.environ['INSTAGRAM_ACCESS_TOKEN']
FACEBOOK_PAGE_ID = "966343003236688"
GRAPH_API_VERSION = "v19.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


def get_instagram_account_id():
    url = f"{BASE_URL}/{FACEBOOK_PAGE_ID}"
    params = {
        'fields': 'instagram_business_account',
        'access_token': INSTAGRAM_ACCESS_TOKEN
    }
    response = requests.get(url, params=params)
    data = response.json()
    ig_id = data.get('instagram_business_account', {}).get('id')
    if not ig_id:
        print(f"Errore get IG account: {data}")
        sys.exit(1)
    print(f"Instagram Account ID trovato: {ig_id}")
    return ig_id


def get_next_post(queue_file="content/queue.json"):
    with open(queue_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    today = datetime.now().strftime("%Y-%m-%d")
    for post in data['posts']:
        if not post['posted'] and post['scheduled_date'] <= today:
            return post, data
    return None, data


def create_media_container(ig_account_id, image_url, caption):
    url = f"{BASE_URL}/{ig_account_id}/media"
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


def publish_media(ig_account_id, container_id):
    url = f"{BASE_URL}/{ig_account_id}/media_publish"
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


def main():
    ig_account_id = get_instagram_account_id()
    post, data = get_next_post()
    if not post:
        print("Nessun post da pubblicare oggi.")
        sys.exit(0)

    print(f"Pubblicando post ID {post['id']}: {post['caption'][:60]}...")

    container_id = create_media_container(ig_account_id, post['image_url'], post['caption'])
    print(f"Container creato: {container_id}")

    media_id = publish_media(ig_account_id, container_id)
    print(f"Post pubblicato! Media ID: {media_id}")

    mark_as_posted(data, post['id'])
    print("Queue aggiornata.")


if __name__ == "__main__":
    main()
