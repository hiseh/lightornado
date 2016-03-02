import time
from datetime import datetime
from enum import IntEnum
from functools import wraps, partial
from unittest import TestCase

from pymongo import MongoClient
from pymongo.errors import AutoReconnect, PyMongoError

from app.baseconfig import MongoConfig

__author__ = 'hisehyin'
__datetime__ = '16/1/18 下午4:28'


class MongoConnections(IntEnum):
    test = 0


class MongoDB:
    def __init__(self):
        self.conn = MongoClient(MongoConfig.path, MongoConfig.port,
                                maxPoolSize=MongoConfig.max_pool_size,
                                waitQueueMultiple=MongoConfig.wait_queue_multiple)
        self.conn.api.authenticate(MongoConfig.user, MongoConfig.password)
        self.db = self.conn.api

    def connect(self, connection_enum):
        if connection_enum in MongoConnections:
            return self.db[connection_enum.name]
        else:
            return None


def decorate_mongo(mongo_db):
    """

    :param mongo_db:
    :return:
    """
    def method_decorator(method):
        @wraps(method)
        def _deco(*args, **kwargs):
            for i in range(5):
                try:
                    mongo = MongoDB().connect(mongo_db)
                    method2 = partial(method, mongo=mongo)
                    return method2(*args, **kwargs)
                except AutoReconnect as e:
                    print(e)
                    time.sleep(pow(2, i) * 0.5)
            raise PyMongoError
        return _deco
    return method_decorator


class Test(TestCase):
    def setUp(self):
        self.start = datetime.now()

    def tearDown(self):
        print(datetime.now() - self.start)

    @decorate_mongo(MongoConnections.test)
    def test_decorate(self, mongo):
        from datetime import timedelta
        coordinates = [123.1, 456.2]
        # result = mongo.update_one({'uid': 1},
        #                           {'$set': {'log': {'type': 'Point', 'coordinates': coordinates}},
        #                            '$currentDate': {'ctime': True}},
        #                           upsert=True)
        result = mongo.find().limit('asdf')
        for e in result:
            print(e['ctime'] + timedelta(hours=8), datetime.now())

