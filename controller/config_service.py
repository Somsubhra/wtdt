import os


class ConfigService:
    def __init__(self):
        pass

    @staticmethod
    def get_env_variable(key):
        try:
            return os.environ[key]
        except Exception as _:
            return None

    @staticmethod
    def get_controller_host():
        return ConfigService.get_env_variable("CONTROLLER_HOST") or "127.0.0.1"

    @staticmethod
    def get_controller_port():
        return ConfigService.get_env_variable("CONTROLLER_PORT") or "8000"

    @staticmethod
    def get_mongo_host():
        return ConfigService.get_env_variable("MONGO_HOST") or "localhost"

    @staticmethod
    def get_controller_env():
        return ConfigService.get_env_variable("CONTROLLER_ENV") or "dev"
