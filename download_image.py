import requests


def download_image(url, path, params=None):
    response = requests.get(url, params, stream=True)
    response.raise_for_status()
    with open(path, 'wb') as image:
        image.write(response.content)