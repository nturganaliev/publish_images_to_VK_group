import os
import requests

from dotenv import load_dotenv
from download_xkcd_image import download_xkcd_image
from download_xkcd_image import get_random_number_for_xkcd


def get_vk_upload_server_url(token, group_id, api_version):
    url = "https://api.vk.com/method/photos.getWallUploadServer"
    params = {
        "access_token": token,
        "group_id": group_id,
        "v": api_version,
    }
    response = requests.get(url, params)
    response.raise_for_status()
    return response.json()['response']['upload_url']


def upload_photo_to_vk_server(upload_url, photo):
    with open(photo, 'rb') as file:
        image = {
            "photo": file,
            "content-type": "multipart/form-data"
        }
        response = requests.post(upload_url, files=image)
    response.raise_for_status()
    upload_response_content = response.json()
    server = upload_response_content['server'],
    photo = upload_response_content['photo'],
    vk_hash = upload_response_content['hash']
    return server, photo, vk_hash


def save_vk_wall_photo(token, group_id, api_version, server, photo, vk_hash):
    url = "https://api.vk.com/method/photos.saveWallPhoto"
    params = {
        "access_token": token,
        "group_id": group_id,
        'server': server,
        'photo': photo,
        'hash': vk_hash,
        "v": api_version,
    }
    response = requests.post(url, params)
    response.raise_for_status()
    response_content = response.json()
    media_id = response_content['response'][0]['id']
    owner_id = response_content['response'][0]['owner_id']
    return f"photo{owner_id}_{media_id}"


def post_photo_to_vk_group(token,
                           group_id,
                           api_version,
                           photo_id,
                           image_text):
    url = "https://api.vk.com/method/wall.post"
    params = {
        "access_token": token,
        "attachments": photo_id,
        "message": image_text,
        "owner_id": f"-{group_id}",
        "from_group": 0,
        "v": api_version,
    }
    response = requests.post(url, params)
    response.raise_for_status()
    return response.json()


def main():
    load_dotenv()

    token = os.getenv('VK_ACCESS_TOKEN')
    group_id = os.getenv('VK_GROUP_ID')
    api_version = os.getenv('VK_API_VERSION')

    try:
        random_number = get_random_number_for_xkcd()
    except requests.exceptions.RequestException as error:
        print(error)
        return

    xkcd_url = f"https://xkcd.com/{random_number}/info.0.json"

    path = os.path.abspath(".")

    try:
        image_path, image_text = download_xkcd_image(xkcd_url, path)
        upload_url = get_vk_upload_server_url(token, group_id, api_version)
        server, photo, vk_hash = upload_photo_to_vk_server(upload_url,
                                                           image_path)
    except requests.exceptions.RequestException as error:
        print(error)
        return
    finally:
        os.remove(image_path)

    try:
        photo_id = save_vk_wall_photo(
                        token,
                        group_id,
                        api_version,
                        server,
                        photo,
                        vk_hash
                    )
    except requests.exceptions.RequestException as error:
        print(error)
        return

    try:
        post_photo_to_vk_group(
            token,
            group_id,
            api_version,
            photo_id,
            image_text
        )
    except requests.exceptions.RequestException as error:
        print(error)
        return


if __name__ == '__main__':
    main()
