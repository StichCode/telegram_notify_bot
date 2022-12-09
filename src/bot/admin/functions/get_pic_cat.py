import requests


async def get_photo_cat() -> bytes | None:
    url = 'https://aws.random.cat/meow'
    # todo: do by aiohttp
    resp = requests.get(url)
    if resp.status_code != 200:
        return None
    meow_photo = resp.json()['file']
    resp = requests.get(meow_photo)
    return resp.content
