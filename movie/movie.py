from dataclasses import dataclass


@dataclass
class MovieDTO:
    id: int
    title: str
    url: str


@dataclass
class Movie:
    id: int
    title: str
    original_title: str
    year: str
    rating: float
    duration: str
    director: str
    actors: list[str]
    countries: list[str]
    genres: list[str]
    url: str
    photo: str

    def convert_to_dto(self) -> MovieDTO:
        return MovieDTO(
            id=self.id,
            title=self.title,
            url=self.url,
        )

    def __str__(self):
        title_with_foreign = f"*{self.title}*{f' / {self.original_title}' if self.original_title else ''}"
        return (f"{title_with_foreign}\n\n"
                f"Год: {self.year}\n"
                f"Рейтинг: {self.rating}\n"
                f"Продолжительность: {self.duration} мин\n"
                f"Режиссер: {self.director}\n"
                f"Актеры: {', '.join(self.actors)}\n\n"
                f"Стран{'ы' if len(self.countries) > 1 else 'а'}: {', '.join(self.countries)}\n"
                f"Жанры: {', '.join(self.genres)}\n"
                f"[Смотреть онлайн]({self.url})")
