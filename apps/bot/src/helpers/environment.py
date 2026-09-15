import os


def is_local_environment():
    return os.getenv("ENVIRONMENT", "DEV") != "PROD"
