import aiohttp
from loguru import logger


async def _get_meows_links(length: int) -> list[str]:
    meows = []
    url = 'https://aws.random.cat/meow'
    async with aiohttp.ClientSession() as session:
        for i in range(length):
            async with session.get(url) as response:
                link = await response.json()
                meows.append(link.get('file', None))
    return meows


async def get_photo_cat(length: int = 60) -> list[bytes]:
    meows = await _get_meows_links(length)
    logger.info("len {}".format(len(meows)))
    images = []
    async with aiohttp.ClientSession() as session:
        for link in meows:
            async with session.get(link) as resp:
                d = await resp.content.read()
                images.append(d)
    return images
