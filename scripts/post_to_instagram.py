import os
import json
import requests
from datetime import datetime
import sys
import time

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


def create_carousel_item_container(ig_account_id, image_url):
    url = f"{BASE_URL}/{ig_account_id}/media"
    params = {
        'image_url': image_url,
        'is_carousel_item': 'true',
        'access_token': INSTAGRAM_ACCESS_TOKEN
    }
    response = requests.post(url, params=params)
    if not response.ok:
        print(f"Errore creazione carousel item: {response.text}")
        response.raise_for_status()
    return response.json()['id']


def create_carousel_container(ig_account_id, children_ids, caption):
    url = f"{BASE_URL}/{ig_account_id}/media"
    params = {
        'media_type': 'CAROUSEL',
        'children': ','.join(children_ids),
        'caption': caption,
        'access_token': INSTAGRAM_ACCESS_TOKEN
    }
    response = requests.post(url, params=params)
    if not response.ok:
        print(f"Errore creazione carousel container: {response.text}")
        response.raise_for_status()
    return response.json()['id']


def is_carousel(post):
    return len(post.get('image_urls', [])) >= 2


def wait_for_container_ready(container_id, max_attempts=10, wait_seconds=5):
    url = f"{BASE_URL}/{container_id}"
    params = {
        'fields': 'status_code,status',
        'access_token': INSTAGRAM_ACCESS_TOKEN
    }
    for attempt in range(1, max_attempts + 1):
        response = requests.get(url, params=params)
        data = response.json()
        status = data.get('status_code', '')
        print(f"Tentativo {attempt}: container status = {status}")
        if status == 'FINISHED':
            return True
        if status == 'ERROR':
            print(f"Errore container: {data}")
            sys.exit(1)
        time.sleep(wait_seconds)
    print("Timeout: container non pronto dopo i tentativi massimi.")
    sys.exit(1)


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


def log_attempt(post_id, container_id, status, log_file="content/post_log.json"):
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            log = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        log = {"attempts": []}
    log["attempts"].append({
        "post_id": post_id,
        "container_id": container_id,
        "status": status,
        "timestamp": datetime.now().isoformat()
    })
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def already_published(post_id, log_file="content/post_log.json"):
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            log = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return False
    return any(
        a["post_id"] == post_id and a["status"] == "success"
        for a in log.get("attempts", [])
    )


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

    if already_published(post['id']):
        print(f"Post ID {post['id']} già pubblicato (log). Aggiorno queue e esco.")
        mark_as_posted(data, post['id'])
        sys.exit(0)

    print(f"Pubblicando post ID {post['id']}: {post['caption'][:60]}...")

    if is_carousel(post):
        print(f"Carosello con {len(post['image_urls'])} immagini")
        children_ids = []
        for i, img_url in enumerate(post['image_urls'], 1):
            print(f"Creando item {i}/{len(post['image_urls'])}: {img_url}")
            child_id = create_carousel_item_container(ig_account_id, img_url)
            print(f"Item {i} container: {child_id}")
            wait_for_container_ready(child_id)
            children_ids.append(child_id)

        container_id = create_carousel_container(ig_account_id, children_ids, post['caption'])
        print(f"Carousel container creato: {container_id}")
        log_attempt(post['id'], container_id, "carousel_container_created")
    else:
        container_id = create_media_container(ig_account_id, post['image_url'], post['caption'])
        print(f"Container creato: {container_id}")
        log_attempt(post['id'], container_id, "container_created")

    wait_for_container_ready(container_id)

    media_id = publish_media(ig_account_id, container_id)
    print(f"Post pubblicato! Media ID: {media_id}")
    log_attempt(post['id'], media_id, "success")

    mark_as_posted(data, post['id'])
    print("Queue aggiornata.")


if __name__ == "__main__":
    main()
