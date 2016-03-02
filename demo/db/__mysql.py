from datetime import datetime
from functools import wraps, partial
from enum import IntEnum
from unittest import TestCase

import pymysql

from app.baseconfig import MySQLConfig

__author__ = 'hisehyin'
__datetime__ = '16/1/19 下午5:42'

"""
pymysql
"""


class PyCursorType(IntEnum):
    list_type = 1
    dict_type = 2


def connect_idoukou_mysql(cursor_type=PyCursorType.list_type):
    cursor_class = {
        PyCursorType.list_type: pymysql.cursors.Cursor,
        PyCursorType.dict_type: pymysql.cursors.DictCursor}[cursor_type]

    conn = pymysql.connect(host=MySQLConfig.host,
                           port=MySQLConfig.port,
                           user=MySQLConfig.user,
                           passwd=MySQLConfig.password,
                           db="music",
                           autocommit=True,
                           charset='utf8',
                           cursorclass=cursor_class)
    return conn


def decorate_pymysql(method):
    @wraps(method)
    def _deco(*args, **kwargs):
        conn = connect_idoukou_mysql(PyCursorType.dict_type)
        try:
            with conn.cursor() as cursor:
                method2 = partial(method,
                                  cursor=cursor)
                return method2(*args, **kwargs)
        finally:
            conn.close()
    return _deco


class Test(TestCase):
    """
    单元测试
    """
    def setUp(self):
        self.start = datetime.now()

    def tearDown(self):
        end = datetime.now()
        print("耗时:\t{hs}".format(hs=end - self.start))

    @decorate_pymysql
    def test_sql(self, **kwargs):
        """

        :param cursor:
        :param kwargs:
        :return:
        """
        sql1 = 'SELECT SQL_CALC_FOUND_ROWS `name` FROM mm_music WHERE is_del = 0 ORDER BY music_id LIMIT 10;'
        sql2 = 'SELECT FOUND_ROWS() as total;'

        cursor = kwargs['cursor']
        cursor.execute(sql1)
        data_source = cursor.fetchall()
        cursor.execute(sql2)
        total = cursor.fetchone()
        print(data_source, total['total'])
        # for e in data_source:
        #     print(e)
