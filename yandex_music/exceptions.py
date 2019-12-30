class BaseError(Exception):
    """Base class for exceptions in this application."""

    pass


class PageNotFoundError(BaseError):
    """Raised if a page does not exist."""

    def __init__(self, msg="Page not found"):
        super().__init__(msg)
        self.code = 404


class InternalServerError(BaseError):
    """Raised if an internal server error occurs."""

    def __init__(self):
        super().__init__("Internal Server Error.")
        self.code = 500


class ArtistNotFoundError(PageNotFoundError):
    """Raised if an artist does not exist."""

    def __init__(self):
        super().__init__("Artist not found.")


class GenreNotFoundError(PageNotFoundError):
    """Raised if a genre does not exist."""

    def __init__(self):
        super().__init__("Genre not found.")


class PlaylistNotFoundError(PageNotFoundError):
    """Raised if a playlist does not exist."""

    def __init__(self):
        super().__init__("Playlist not found.")


class UserNotFoundError(PageNotFoundError):
    """Raised if a user does not exist."""

    def __init__(self):
        super().__init__("User not found.")
