import os
import requests

from dotenv import load_dotenv
from download_xkcd_image import download_xkcd_image
from download_xkcd_image import get_random_number_for_xkcd


def get_vk_upload_server_url(url, params):
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
    return [
        upload_response_content['server'],
        upload_response_content['photo'],
        upload_response_content['hash'],
    ]


def save_vk_wall_photo(url, params):
    response = requests.post(url, params)
    response.raise_for_status()
    response_content = response.json()
    media_id = response_content['response'][0]['id']
    owner_id = response_content['response'][0]['owner_id']
    return f"photo{owner_id}_{media_id}"


def post_photo_to_vk_group(url, params):
    response = requests.post(url, params)
    response.raise_for_status()
    return response.json()


def main():
    load_dotenv()

    token = os.getenv('VK_ACCESS_TOKEN')
    group_id = os.getenv('VK_GROUP_ID')
    api_version = os.getenv('VK_API_VERSION')

    vk_url = "https://api.vk.com/method/"
    methods = [
        'photos.getWallUploadServer',
        'photos.saveWallPhoto',
        'wall.post',
    ]
    params = {
        "access_token": token,
        "group_id": group_id,
        "v": api_version,
    }

    try:
        random_number = get_random_number_for_xkcd()
    except requests.exceptions.RequestException as error:
        return error

    xkcd_url = f"https://xkcd.com/{random_number}/info.0.json"

    path = os.path.abspath(".")

    try:
        image_path, image_text = download_xkcd_image(xkcd_url, path)
        upload_url = get_vk_upload_server_url(f"{vk_url}/{methods[0]}",
                                              params)
        server, photo, vk_hash = upload_photo_to_vk_server(upload_url,
                                                           image_path)
    except requests.exceptions.RequestException as error:
        return error
    finally:
        os.remove(image_path)

    params.update({
        'server': server,
        'photo': photo,
        'hash': vk_hash,
    })

    try:
        photo_id = save_vk_wall_photo(f"{vk_url}/{methods[1]}", params)
    except requests.exceptions.RequestException as error:
        return error

    wall_post_params = {
        "access_token": token,
        "attachments": photo_id,
        "message": image_text,
        "owner_id": f"-{group_id}",
        "from_group": 0,
        "v": api_version,
    }

    try:
        post_photo_to_vk_group(f"{vk_url}/{methods[2]}", wall_post_params)
    except requests.exceptions.RequestException as error:
        return error


if __name__ == '__main__':
    main()
