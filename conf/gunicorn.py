from psycogreen.gevent import patch_psycopg


def post_fork(server, worker):
    patch_with_psycogreen_gevent()
    worker.log.info("Enabled async Psycopg2")


def patch_with_psycogreen_gevent():
    patch_psycopg()
