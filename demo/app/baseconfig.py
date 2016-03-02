from multiprocessing import cpu_count

from tornado.options import options

__author__ = 'hisehyin'
__datetime__ = '16/1/14 下午12:16'

options.parse_command_line()
try:
    DEBUG = options.debug == 1
except AttributeError:
    DEBUG = True


class BaseConfig(object):
    """
    全局设定
    """
    if DEBUG:
        cpu_count = 1
        pic_host = "http://192.168.0.61"
        static_host = "http://static01.idoukou.com"
    else:
        cpu_count = cpu_count()
        pic_host = "http://pic.idoukou.com"
        static_host = "http://static.idoukou.com"

    tmp_path = 'tmp'
    log_path = './logs'
    user_icon_url = "avatar/{uid}/big.jpg"
    m_idoukou_home = "http://m.idoukou.com"
    php_path = "php"
    match_path = "match"
    lottery_path = "lottery"
    cache_expired_date = 15
    aes_expired_date = 30
    request_expired_second = 5
    page_size = 20
    earth_radius = 6371.004
    max_handler_thread = 100


class RedisConfig:
    if DEBUG:
        host = "192.168.0.72"
        port = 5379
        password = 'RedIs-sErver_tEsteR'
        max_connections = 10
    else:
        host = "192.168.0.72"
        port = 5379
        password = "RedIs-sErver_tEsteR"
        max_connections = 10


# mysql 数据库
class MySQLConfig:
    if DEBUG:
        host = "192.168.0.75"
        # self.host = "112.124.45.1"
        port = 3306
        user = "web_root"
        # self.user = "Mr_Yin"
        password = "music_mysql!"
        # self.password = "YINsHu-jinG@_2015"
        max_connections = 10
        timeout = 1
    else:
        host = "10.160.47.75"
        # self.host = "10.160.47.75"
        port = 3306
        user = "python-use"
        password = "python-user@123456"
        max_connections = 1000
        timeout = 300


# mongodb
class MongoConfig:
    if DEBUG:
        path = "192.168.0.61"
        port = 27017
        user = "python-user"
        password = "music_mongo!"
        max_pool_size = 20
        wait_queue_multiple = 10
    else:
        path = "localhost"
        port = 27017
        user = "python-user"
        password = "music_mongo!"
        max_pool_size = 200
        wait_queue_multiple = 100


# 短信网关
class SmsGate:
    url = "http://inolink.com/WS/Send2.aspx"
    username = "TCLKJ02238"
    password = "music-admin"
