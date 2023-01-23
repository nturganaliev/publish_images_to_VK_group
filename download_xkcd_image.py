import os
import random
import requests

from urllib.parse import urlparse
from urllib.parse import unquote


def get_file_extension_from_url(url):
    filename = unquote(urlparse(url).path.split("/")[-1])
    return os.path.splitext(filename)[-1]


def get_random_number_for_xkcd():
    url = "https://xkcd.com/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    last_image_number = response.json()["num"]
    return random.randint(1, last_image_number)


def download_xkcd_image(url, path):
    response = requests.get(url)
    response.raise_for_status()
    response_content = response.json()
    image_url = response_content["img"]
    title = response_content["title"].lower()
    extension = get_file_extension_from_url(image_url)
    text = response_content['alt']
    image_path = os.path.join(path, f"{title}{extension}")
    image_response = requests.get(image_url, stream=True)
    image_response.raise_for_status()
    
    with open(image_path, 'wb') as image:
        image.write(image_response.content)

    return image_path, text
