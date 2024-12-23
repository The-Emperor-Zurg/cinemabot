from aiohttp import ClientSession
from bs4 import BeautifulSoup
from urllib.parse import quote

from movie import Movie


class KinopoiskProvider:
    def __init__(self, token: str):
        self.token = token

    async def _parse_movie(self, session: ClientSession, movie_id: int) -> Movie | None:
        """Запрашивает информацию о фильме по ID через API"""
        headers = {
            'X-API-KEY': self.token,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        url = f"https://kinopoiskapiunofficial.tech/api/v2.2/films/{movie_id}"
        async with session.get(url, headers=headers) as r:
            if r.status != 200:
                return None

            information = await r.json()
            return Movie(
                id=movie_id,
                title=information["nameRu"],
                original_title=information["nameOriginal"],
                year=information["year"],
                rating=information["ratingKinopoisk"],
                duration=information["filmLength"],
                director="-",
                actors=list(),
                countries=[i["country"] for i in information["countries"]],
                genres=[i["genre"] for i in information["genres"]],
                url=f"https://flicksbar.mom/film/{movie_id}",
                photo=information["posterUrl"]
            )

    async def get_movie(self, query: str) -> Movie | None:
        """Ищет фильм по названию и возвращает информацию о нём"""
        url = f"https://www.kinopoisk.ru/index.php?kp_query={quote(query)}"

        async with ClientSession() as session:
            async with session.get(url) as r:
                if r.status != 200:
                    if len(query) > 10:
                        return await self.get_movie(query[:10])
                    return None

                html = await r.text()
                bs = BeautifulSoup(html, "html.parser")

                movie_link = bs.select_one("div.element.most_wanted > .info > .name > a")
                if not movie_link:
                    return None

                movie = await self._parse_movie(session, int(movie_link["data-id"]))
                if not movie:
                    if len(query) > 10:
                        return await self.get_movie(query[:10])
                    return None

                director_tag = bs.select_one("div.element.most_wanted > .info .director > a")
                if director_tag:
                    movie.director = director_tag.text

                actors_tags = bs.select("div.element.most_wanted > .info > .gray:nth-child(4) .lined")
                if actors_tags:
                    movie.actors = [tag.text for tag in actors_tags]

                return movie
