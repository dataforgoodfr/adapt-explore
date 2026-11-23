from common.base import BaseDriver


class ApiDriver(BaseDriver):
    """Source via API HTTP."""

    def validate_config(self, config: dict) -> None:
        raise NotImplementedError

    def fetch(self, config: dict, since: str | None = None):
        raise NotImplementedError

    def healthcheck(self, config: dict) -> bool:
        raise NotImplementedError