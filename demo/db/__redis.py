from datetime import datetime
from enum import IntEnum
from functools import wraps, partial
from unittest import TestCase

from redis import Redis, ConnectionPool

from app.baseconfig import RedisConfig

__author__ = 'hisehyin'
__datetime__ = '16/1/18 上午11:03'


class RedisDB(IntEnum):
    """
    db distribute
    """
    test = 0


class RedisConnectionPool(object):
    """
    连接池
    """
    def __init__(self, db):
        """
        连接设置
        :param db:
        :return:
        """
        self.connection_kwargs = dict(host=RedisConfig.host,
                                      port=RedisConfig.port,
                                      password=RedisConfig.password,
                                      db=db.value,
                                      max_connections=RedisConfig.max_connections)

    def get_connection_pool(self):
        pool = ConnectionPool(**self.connection_kwargs)
        return pool

    def get_redis_client(self):
        pool = self.get_connection_pool()
        return Redis(connection_pool=pool)


def decorate_redis(redis_db):
    """

    :param redis_db:
    :return:
    """
    def method_decorator(method):
        @wraps(method)
        def _deco(*args, **kwargs):
            redis = RedisConnectionPool(redis_db).get_redis_client()
            method2 = partial(method, redis=redis)
            return method2(*args, **kwargs)
        return _deco
    return method_decorator


class Test(TestCase):
    def setUp(self):
        self.start = datetime.now()

    def tearDown(self):
        print(datetime.now() - self.start)

    def test_pool_connect(self):
        redis = RedisConnectionPool(RedisDB.test).get_redis_client()
        self.assertTrue(isinstance(redis, Redis))

    @decorate_redis(RedisDB.match)
    def test_uese(self, redis):
        from re import compile
        match_partner = compile(r'(match:\d+round:\d+player|list)+')
        # match_partner = compile(r"(match:)([0-9]+)(round:)(]0-9]+)*")

        for key in redis.keys():
            key = key.decode('utf-8')
            if match_partner.match(key):
                print(key)
