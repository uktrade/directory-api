import os


def is_local():
    return os.getenv('APP_ENVIRONMENT') is None


def is_circleci():
    return 'CIRCLECI' in os.environ


def get_env_files():
    return ['conf/env/' + filename for filename in os.getenv('ENV_FILES', '').split(',')]
