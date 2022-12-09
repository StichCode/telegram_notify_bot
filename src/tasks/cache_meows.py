from dependency_injector.wiring import Provide, inject

from src.bot.functions.get_pic_cat import get_photo_cat
from src.container import Container
from src.storage.simple_cache import MeowCache


@inject
async def cache_meows_task(cache: MeowCache = Provide[Container.meow]) -> None:
    data = await get_photo_cat()
    cache.add(data)