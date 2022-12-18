import logging

import aiohttp

from config import Config


class PostcardsClient:
    def __init__(self):
        self.link = Config.POSTCARDS_HOST

    async def _get_json(self, route: str, params: dict | None) -> dict:
        """
        Send get request to host
        :param route: request link
        :return: json object answer from host
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.link}{route}',
                                   params=params if params is not None else {}) as resp:
                logging.info(f"{resp.status=} {self.link}{route} {params=}")
                return await resp.json()

    async def _get_file(self, route: str, params: dict | None) -> bytes:
        """
        Download file from server
        :param route: request link
        :param params: parameters of file
        :return: file in bytes
        """
        # async with aiohttp.ClientSession(headers={"Authorization": f"Bearer {Config.token}"}) as session:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f'{self.link}{route}',
                    params=params if params is not None else {}
            ) as resp:
                logging.info(f"{resp.status=} {self.link}{route} {params=}")
                return await resp.read()

    async def get_postcard(self, text: str, category: str, template: str):
        params = {
            "text": text,
            "category": category,
            "template": template
        }
        return await self._get_file("/postcard", params)

    async def get_postcards_types(self) -> list:
        list_of_types = await self._get_json("/categories", None)
        return list_of_types['data']

    async def get_postcards_list_by_type(self, category: str) -> list:
        params = {
            "category": category
        }
        list_of_postcards = await self._get_json("/postcards", params)
        return list_of_postcards['data']

    async def get_preview(self, category: str, template: str):
        params = {
            "category": category,
            "template": template
        }
        return await self._get_file("/preview", params)
