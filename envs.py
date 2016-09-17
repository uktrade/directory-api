"""Creates .env files for docker-compose"""
import os
import sys


def get_unset_host_env_vars(env_vars):
    return [var for var in env_vars if not os.getenv(var)]


def write_env_file(file_path, host_to_docker_env_vars):
    with open(file_path, 'w') as dest:
        for host_env_var, docker_env_var in host_to_docker_env_vars.items():
                dest.write(
                    "{docker_env_var}={host_env_var}\n".format(
                        docker_env_var=docker_env_var,
                        host_env_var=os.getenv(host_env_var),
                    )
                )


def create_env_files(docker_environments):
    unset_host_vars = []
    for env in docker_environments:
        unset_host_vars += get_unset_host_env_vars(
            env_vars=env['host_to_docker_env_vars']
        )

    if unset_host_vars:
        sys.exit(
            "Required host environment variables are not set: \n{}".format(
                "\n".join(unset_host_vars)
            )
        )
    else:
        for env in docker_environments:
            write_env_file(env['file_path'], env['host_to_docker_env_vars'])


def set_host_envs_for_running_locally():
        host_test_env_vars = {
            'DIRECTORY_FORM_DATA_SECRET_KEY': 'test',
            'DIRECTORY_FORM_DATA_POSTGRES_USER': 'test',
            'DIRECTORY_FORM_DATA_POSTGRES_PASSWORD': 'test',
            'DIRECTORY_FORM_DATA_POSTGRES_DB': 'directory-form-data-test',
            'DIRECTORY_FORM_DATA_POSTGRES_USER': 'test',
            'DIRECTORY_FORM_DATA_DATABASE_URL': (
                'postgres://test:test@postgres:5432/directory-form-data-test'
            )
        }
        for env_var, value in host_test_env_vars.items():
            os.environ[env_var] = value

if __name__ == '__main__':

    if os.getenv('DIRECTORY_FORM_DATA_RUNNING_LOCALLY') == 'true':
        set_host_envs_for_running_locally()

    create_env_files(docker_environments=[
        {
            'file_path': '.env',
            'host_to_docker_env_vars': {
                'DIRECTORY_FORM_DATA_SECRET_KEY': 'SECRET_KEY',
                'DIRECTORY_FORM_DATA_DATABASE_URL': 'DATABASE_URL',
                'DIRECTORY_FORM_DATA_AWS_ACCESS_KEY_ID': 'AWS_ACCESS_KEY_ID',
                'DIRECTORY_FORM_DATA_AWS_SECRET_ACCESS_KEY': (
                    'AWS_SECRET_ACCESS_KEY'
                ),
            }
        },
        {
            'file_path': '.env-postgres',
            'host_to_docker_env_vars': {
                'DIRECTORY_FORM_DATA_POSTGRES_USER': 'POSTGRES_USER',
                'DIRECTORY_FORM_DATA_POSTGRES_PASSWORD': 'POSTGRES_PASSWORD',
                'DIRECTORY_FORM_DATA_POSTGRES_DB': 'POSTGRES_DB',
            }
        },
    ])
