import os
import requests

from dotenv import load_dotenv

import fetch_xkcd_images


def main():
    load_dotenv()

    image_name = fetch_xkcd_images
    token = os.getenv('VK_ACCESS_TOKEN')
    group_id = os.getenv('VK_GROUP_ID')
    api_version = os.getenv('VK_API_VERSION')
    methods = ['photos.getWallUploadServer',
               'photos.saveWallPhoto',
               'wall.post']
    url = f"https://api.vk.com/method/"
    params = {
        "access_token": token,
        "group_id": group_id,
        "v": api_version,
    }


    server_response = requests.get(f"{url}{methods[0]}", params)
    server_response.raise_for_status()
    upload_url = server_response.json()['response']['upload_url']
    with open('reverse_identity_theft.png', 'rb') as file:
        image = {
            "photo": file,
            "content-type": "multipart/form-data"
        }
        upload_response = requests.post(upload_url, files=image)

    upload_response_content = upload_response.json()
    params = {
        "access_token": token,
        'server': upload_response_content['server'],
        'photo': upload_response_content['photo'],
        'hash': upload_response_content['hash'],
        "group_id": group_id,
        "v": api_version,
    }

    save_response = requests.post(f"{url}{methods[1]}", params)
    save_response_content = save_response.json()
    image_url = save_response_content['response'][0]['sizes'][2]['url']
    owner_id = save_response_content['response'][0]['owner_id']
    media_id = save_response_content['response'][0]['id']
    print()
    print(image_url)
    with open('reverse_identity_theft.txt', 'r') as f:
        comment = f.read()

    photo_id = f"photo{owner_id}_{media_id},{image_url}"
    params = {
        "access_token": token,
        "attachements": image_url,
        "message": comment,
        "owner_id": f"-{group_id}",
        "from_group": 0,
        "v": api_version,
    }

    post_url = f"https://api.vk.com/method/{methods[2]}"
    post_response = requests.post(post_url, params)
    print(post_response.json())

if __name__ == '__main__':
    main()