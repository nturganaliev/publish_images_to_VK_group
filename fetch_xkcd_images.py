import os
import random
import requests

from download_image import download_image
from get_file_extension_from_url import get_file_extension_from_url


def get_random_number_for_xkcd():
    url = "https://xkcd.com/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    last_image_number = response.json()["num"]
    return random.randint(1, last_image_number)


def main():
    random_number = get_random_number_for_xkcd()
    url = f"https://xkcd.com/{random_number}/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    response_content = response.json()
    image_url = response_content["img"]
    image_name = response_content["title"].lower()
    image_extension = get_file_extension_from_url(image_url)
    path = os.path.join(os.path.abspath("."), f"{image_name}{image_extension}")
    try:
        download_image(image_url, path)
    except requests.exceptions.RequestException as error:
        print(error)
    print(response_content["alt"])
    with open(f'{image_name}.txt', 'w') as file:
        file.write(response_content['alt'])
    print("Завершение работы.")




if __name__ == '__main__':
    main()
