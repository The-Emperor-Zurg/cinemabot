from dataclasses import dataclass

from .movie import Movie, MovieDTO
from sqlite import SqliteProvider
from .kinopoisk import KinopoiskProvider

@dataclass
class MovieManager:
    db_provider: SqliteProvider
    kp_provider: KinopoiskProvider

    async def fetch_and_store_movie(self, query: str | None, user_id: int) -> Movie | None:
        if query is None:
            return None

        movie = await self.kp_provider.get_movie(query)
        if movie is None:
            return None

        await self.db_provider.insert_movie(movie)
        await self.db_provider.write_query(user_id, movie.id)

        return movie

    async def retrieve_user_history (self, user_id):
        return await self.db_provider.get_queries_by_user_id(user_id)

    async def compile_user_statistics(self, user_id) -> list[tuple[MovieDTO, int]]:
        return await self.db_provider.fetch_user_query_statistics(user_id)
