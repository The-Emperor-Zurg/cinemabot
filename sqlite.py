import aiosqlite

from movie import MovieDTO


class SqliteProvider:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def _execute_nonquery(self, query: str, parameters: tuple = ()):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(query, parameters)
            await db.commit()

    async def _execute_and_fetch(self, query: str, parameters: tuple = ()):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(query, parameters) as cursor:
                await db.commit()
                return await cursor.fetchall()

    @staticmethod
    def _convert_to_movie_dto(row: tuple) -> MovieDTO:
        return MovieDTO(
            id=row[0],
            title=row[1],
            url=row[2],
        )

    async def initialize_tables(self) -> None:
        await self._execute_nonquery("""
            CREATE TABLE IF NOT EXISTS user_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                movie_id INTEGER NOT NULL
            );
        """)

        await self._execute_nonquery("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id INTEGER UNIQUE NOT NULL,
                title VARCHAR NOT NULL,
                url VARCHAR NOT NULL
            );
        """)

    async def fetch_movie_by_id(self, movie_id: int) -> MovieDTO | None:
        rows = await self._execute_and_fetch("SELECT movie_id, title, url FROM movies WHERE movie_id = ?", (movie_id,))
        if not rows:
            return None
        return self._convert_to_movie_dto(rows[0])

    async def insert_movie(self, movie: MovieDTO) -> None:
        if await self.fetch_movie_by_id(movie.id) is None:
            await self._execute_nonquery(
                "INSERT INTO movies (movie_id, title, url) VALUES (?, ?, ?);",
                (movie.id, movie.title, movie.url)
            )

    async def get_queries_by_user_id(self, user_id: int) -> list[MovieDTO]:
        rows = await self._execute_and_fetch("""
            SELECT t2.movie_id as movie_id, t2.title as title, t2.url as url
            FROM user_queries as t1
            JOIN movies AS t2 ON t1.movie_id = t2.movie_id
            WHERE t1.user_id = ?
            ORDER BY t1.id DESC
            LIMIT 5
        """,(user_id,)
        )
        return [self._convert_to_movie_dto(row) for row in rows]

    async def fetch_user_query_statistics(self, user_id: int) -> list[tuple[MovieDTO, int]]:
        rows = await self._execute_and_fetch("""
            SELECT t2.movie_id as movie_id, t2.title as title, t2.url as url, COUNT(*)
            FROM user_queries as t1
            JOIN movies AS t2 ON t1.movie_id = t2.movie_id
            WHERE t1.user_id = ?
            GROUP BY t2.movie_id
            ORDER BY COUNT(*) DESC
        """, (user_id,))
        return [(self._convert_to_movie_dto(row), row[3]) for row in rows]

    async def write_query(self, user_id: int, movie_id: int) -> None:
        await self._execute_nonquery(
            "INSERT INTO user_queries (user_id, movie_id) VALUES (?, ?);",
            (user_id, movie_id)
        )
