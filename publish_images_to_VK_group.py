import os
import random
import requests
import time

from download_image import download_image
from get_file_extension_from_url import get_file_extension_from_url

from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv('VK_ACCESS_TOKEN')
GROUP_ID = os.getenv('VK_GROUP_ID')
API_VERSION = os.getenv('VK_API_VERSION')       


def get_vk_upload_server_url():
    url = "https://api.vk.com/method/photos.getWallUploadServer"
    params = {
        "access_token": TOKEN,
        "group_id": GROUP_ID,
        "v": API_VERSION,
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
    return response


def save_vk_wall_photo(server, photo, vk_hash):
    url = "https://api.vk.com/method/photos.saveWallPhoto"
    params = {
        "access_token": TOKEN,
        "group_id": GROUP_ID,
        "v": API_VERSION,
        'server': server,
        'photo': photo,
        'hash': vk_hash,
    }
    response = requests.post(url, params)
    response.raise_for_status()
    return response


def get_vk_wall_photo_id(response):
    response_content = response.json()
    owner_id = response_content['response'][0]['owner_id']
    media_id = response_content['response'][0]['id']
    return f"photo{owner_id}_{media_id}"


def post_photo_to_vk_group(photo_id, text):
    url = "https://api.vk.com/method/wall.post"
    params = {
        "access_token": TOKEN,
        "attachments": photo_id,
        "message": text,
        "owner_id": f"-{GROUP_ID}",
        "from_group": 0,
        "v": API_VERSION,
    }
    response = requests.post(url, params)
    response.raise_for_status()
    return response.json()


def get_random_number_for_xkcd():
    url = "https://xkcd.com/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    last_image_number = response.json()["num"]
    return random.randint(1, last_image_number)


def main():
    try:
        random_number = get_random_number_for_xkcd()
    except requests.exceptions.RequestException as error:
        print(error)
    
    url = f"https://xkcd.com/{random_number}/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    response_content = response.json()
    image_url = response_content["img"]
    image_name = response_content["title"].lower()
    image_extension = get_file_extension_from_url(image_url)
    image_text = response_content['alt']
    path = os.path.join(os.path.abspath("."), f"{image_name}{image_extension}")
    
    try:
        download_image(image_url, path)
        upload_url = get_vk_upload_server_url()
        upload_response = upload_photo_to_vk_server(upload_url, path)
    except requests.exceptions.RequestException as error:
        print(error)

    upload_response_content = upload_response.json()
    server = upload_response_content['server'],
    photo = upload_response_content['photo'],
    vk_hash = upload_response_content['hash'],

    try:
        save_response = save_vk_wall_photo(server, photo, vk_hash)
    except requests.exceptions.RequestException as error:
        print(error)

    photo_id = get_vk_wall_photo_id(save_response)

    try:
        post_photo_to_vk_group(photo_id, image_text)
    except requests.exceptions.RequestException as error:
        print(error)

    time.sleep(10)

    if not os.path.exists(path):
        print("Файл не существует.")
        print("Завершение работы.")
        return
    os.remove(path)
    print("Завершение работы.")


if __name__ == '__main__':
    main()
