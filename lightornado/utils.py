import base64
import collections
import calendar
import hashlib
import os
import random
import string
from datetime import datetime, timedelta
from enum import IntEnum
from hashlib import md5
from os import kill, getpid
from signal import SIGKILL
from subprocess import Popen, PIPE
from unittest import TestCase

from tornado import escape

if 'Darwin' in os.uname():
    import sys
    import crypto
    sys.modules["Crypto"] = crypto

from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA

__author__ = 'hisehyin'
__datetime__ = '16/1/18 上午11:41'


def shutdown_process(name):
    """
    杀掉指定进程
    :param name: 进程名
    :return:
    """
    p = Popen(['ps', '-ef'], stdout=PIPE)
    out, err = p.communicate()
    for line in out.splitlines():
        try:
            line_str = line.decode('utf-8')
        except UnicodeDecodeError:
            continue

        if name in line_str:
            pid = int(line.split()[1])
            if pid != getpid():
                kill(pid, SIGKILL)


def convert2str(data):
    if isinstance(data, bytes):
        return str(data.decode('utf-8'))
    elif isinstance(data, str):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert2str, data.items()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert2str, data))
    else:
        return data


def mcmd5(plain_text):
    md5_obj = md5()
    md5_obj.update(plain_text.encode("utf-8"))
    return md5_obj.hexdigest()


def sha512_password(plain_text, salt):
    """
    sha512加密
    :param plain_text:
    :param salt:
    :return:
    """
    sha512_object = hashlib.sha512()
    sha512_object.update(salt.encode("utf-8"))
    sha512_object.update(plain_text.encode("utf-8"))
    encrypted_password = "sha512" + "$" + salt + "$" + sha512_object.hexdigest()
    return encrypted_password


class MCAES(object):
    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_ECB
        self.bs = 16
        self.pad = lambda s: s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)
        self.un_pad = lambda s: s[:-ord(s[len(s) - 1:])]

    def encrypt(self, plaintext):
        plaintext = self.pad(plaintext)
        cipher = AES.new(self.key, self.mode)
        return base64.b64encode(cipher.encrypt(plaintext)).decode("utf-8")

    def decrypt(self, base64text):
        encrypt_data = base64.b64decode(base64text)
        cipher = AES.new(self.key, self.mode)
        try:
            return self.un_pad(cipher.decrypt(encrypt_data)).decode("utf-8")
        except ValueError:
            return None


class RandomStringType(IntEnum):
    only_alphabet = 0
    digit_alphabet = 1
    ascii_code = 2
    only_digit = 3


class MCDate(object):
    @staticmethod
    def curr_week(today):
        """
        本周
        :param today:
        :return:
        """
        start = datetime.combine(today - timedelta(days=today.weekday()), datetime.min.time())
        end = datetime.combine(today + timedelta(days=(6 - today.weekday())), datetime.max.time())
        return [start, end]

    @staticmethod
    def last_week(today):
        """
        上周周期
        :param today:
        :return:
        """
        start_base_day = today - timedelta(days=today.weekday(), weeks=1)
        end_base_day = start_base_day + timedelta(days=6)

        start = datetime.combine(start_base_day, datetime.min.time())
        end = datetime.combine(end_base_day, datetime.max.time())
        return [start, end]

    @staticmethod
    def curr_month(today):
        """
        当前月
        :param today:
        :return:
        """
        start = datetime.combine(today.replace(day=1), datetime.min.time())
        end = datetime.combine(today.replace(day=calendar.monthrange(today.year, today.month)[1]), datetime.max.time())
        return [start, end]

    @staticmethod
    def last_month(today):
        """
        上月周期
        :param today:
        :return:
        """
        end_base_day = today.replace(day=1) - timedelta(days=1)

        start = datetime.combine(end_base_day.replace(day=1), datetime.min.time())
        end = datetime.combine(end_base_day, datetime.max.time())
        return [start, end]

    @staticmethod
    def curr_quarter(today):
        """
        current quarter
        :param today:
        :return:
        """
        quarter_num = (today.month - 1) // 3
        start = datetime.strptime('{year}-{month}-1'.format(year=today.year, month=quarter_num * 3 + 1),
                                  '%Y-%m-%d')
        end = datetime.strptime('{year}-{month}-{day} 23:59:59.999999'
                                .format(year=today.year,
                                        month=start.month + 2,
                                        day=calendar.monthrange(today.year, start.month + 2)[1]),
                                '%Y-%m-%d %H:%M:%S.%f')
        return [start, end]

    @staticmethod
    def last_quarter(today):
        """
        上一季
        :param today:
        :return:
        """
        quarter_num = (today.month - 1) // 3
        if quarter_num == 0:
            # 上一年
            today = today.replace(year=today.year - 1, month=12)
            quarter_num = 4

        start = datetime.strptime('{year}-{month}-1'.format(year=today.year, month=(quarter_num - 1) * 3 + 1),
                                  '%Y-%m-%d')
        end = datetime.strptime('{year}-{month}-{day} 23:59:59.999999'
                                .format(year=today.year,
                                        month=start.month + 2,
                                        day=calendar.monthrange(today.year, start.month + 2)[1]),
                                '%Y-%m-%d %H:%M:%S.%f')
        return [start, end]

    @staticmethod
    def curr_year(today):
        """
        current year
        :param today:
        :return:
        """
        base_year = today.year

        return [datetime.strptime('{year}-1-1'.format(year=base_year), '%Y-%m-%d'),
                datetime.strptime('{year}-12-31 23:59:59.999999'.format(year=base_year), '%Y-%m-%d %H:%M:%S.%f')]

    @staticmethod
    def last_year(today):
        """
        上一年
        :param today:
        :return:
        """
        base_year = today.year - 1

        return [datetime.strptime('{year}-1-1'.format(year=base_year), '%Y-%m-%d'),
                datetime.strptime('{year}-12-31 23:59:59.999999'.format(year=base_year), '%Y-%m-%d %H:%M:%S.%f')]


def random_string(random_type=RandomStringType.ascii_code, length=16):
    """
    Returns a new string with random char
    :param random_type: random char type
    :param length: the new string length
    :return: the new string
    """
    chars = {
        "only_alphabet": string.ascii_letters,
        "digit_alphabet": string.ascii_letters + string.digits,
        "ascii_code": string.ascii_letters + string.digits + string.punctuation,
        "only_digit": string.digits
    }[random_type.name]
    result = ''.join(random.choice(chars) for _ in range(length))
    return result


def rsa_encrypt(public_key, message):
    """
    RSA加密
    :param public_key:
    :param message:
    :return:
    """
    try:
        rsa_key = RSA.importKey(public_key)
    except ValueError:
        return None

    if rsa_key.can_encrypt():
        plant_text = message.encode("utf-8")
        rsa = PKCS1_v1_5.new(rsa_key)
        encrypted = rsa.encrypt(plant_text)
        return base64.b64encode(encrypted).decode("utf-8")
    else:
        return None


def object_name(cls):
    """
    返回import路径
    :param cls:
    :return:
    """
    return '{module}.{class_name}'.format(module=cls.__module__,
                                          class_name=cls.__name__)


class Test(TestCase):
    def setUp(self):
        self.aes = MCAES("b}bLyOk\"-8Vc,;'`")
        self.plain_text = {"stamp": "1442471740.409927",
                           "page": 0,
                           "page_size": 40,
                           "current_uid": 500000048}
        self.public_key = "-----BEGIN PUBLIC KEY-----\r\n" \
                          "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCmUyNySLbGqJ6SH90SYxbSlaHk\r\n" \
                          "LpXvgp2IU4XftyLptUcOFS3NluqmISlmbsRfA455vAI1SfRV3mOkPNZZvUxeUI0z\r\n" \
                          "yD4/d5MDL408+Pdv/jHSmTqEcsZvyg+nJlWQ7AJg2+rxID8CDKVjmx/UpEtLv4pP\r\n" \
                          "+re0AnyU5JLskqFaaQIDAQAB\r\n" \
                          "-----END PUBLIC KEY-----"

    def test_aes(self):
        encrypted_text = ("aAw6G64E02eNad6whfRR7fPIO971qJKeej/ElB5MGPjEbGD0xRDkPV5Su96u4TNF\n"
                          "VAQ/WcCF9MirTehqS3B9SpI0Rwr+k6QBSLFovnFiYKk=")
        self.assertEqual(escape.json_decode(self.aes.decrypt(encrypted_text)), self.plain_text)

    def test_rsa(self):
        result = rsa_encrypt(public_key=self.public_key, message="hello")
        print(result)
        self.assertTrue(result, msg="RSA encrypt")


class TestDate(TestCase):
    def setUp(self):
        self.day1 = datetime.strptime('{year}-{month}-{day}'.format(year=2015, month=11, day=23),
                                      '%Y-%m-%d').date()
        self.day2 = self.day1.replace(month=12, day=1)
        self.day3 = datetime.strptime('{year}-{month}-{day}'.format(year=2016, month=1, day=1),
                                      '%Y-%m-%d').date()
        self.day4 = datetime.strptime('{year}-{month}-{day}'.format(year=2016, month=1, day=4),
                                      '%Y-%m-%d').date()
        self.start = datetime.now()

    def tearDown(self):
        print(datetime.now() - self.start)

    def test_curr_week(self):
        # 2015-11-23
        result1 = MCDate.curr_week(self.day1)
        print(result1[0].timestamp())
        self.assertEqual(result1[0], datetime.strptime('2015-11-23', '%Y-%m-%d'))
        self.assertEqual(result1[1], datetime.strptime('2015-11-29 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

        # 2015-12-1
        result2 = MCDate.curr_week(self.day2)
        self.assertEqual(result2[0],
                         datetime.strptime('2015-11-30', '%Y-%m-%d'))
        self.assertEqual(result2[1],
                         datetime.strptime('2015-12-6 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

        # 2016-1-1
        result3 = MCDate.curr_week(self.day3)
        self.assertEqual(result3[0],
                         datetime.strptime('2015-12-28', '%Y-%m-%d'))
        self.assertEqual(result3[1],
                         datetime.strptime('2016-1-3 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

        # 2016-1-4
        result4 = MCDate.curr_week(self.day4)
        self.assertEqual(result4[0],
                         datetime.strptime('2016-1-4', '%Y-%m-%d'))
        self.assertEqual(result4[1],
                         datetime.strptime('2016-1-10 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

    def test_last_week(self):
        # 2015-11-23
        result1 = MCDate.last_week(self.day1)
        self.assertEqual(result1[0].timestamp(), 1447603200.0)
        self.assertEqual(result1[1].timestamp(), 1448207999.999999)

        # 2015-12-1
        result2 = MCDate.last_week(self.day2)
        self.assertEqual(result2[0],
                         datetime.strptime('2015-11-23', '%Y-%m-%d'))
        self.assertEqual(result2[1],
                         datetime.strptime('2015-11-29 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

        # 2016-1-1
        result3 = MCDate.last_week(self.day3)
        self.assertEqual(result3[0],
                         datetime.strptime('2015-12-21', '%Y-%m-%d'))
        self.assertEqual(result3[1],
                         datetime.strptime('2015-12-27 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

        # 2016-1-4
        result4 = MCDate.last_week(self.day4)
        self.assertEqual(result4[0],
                         datetime.strptime('2015-12-28', '%Y-%m-%d'))
        self.assertEqual(result4[1],
                         datetime.strptime('2016-1-3 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

    def test_curr_month(self):
        # 2015-11-23
        result1 = MCDate.curr_month(self.day1)
        self.assertEqual(result1[0],
                         datetime.strptime('2015-11-1', '%Y-%m-%d'))
        self.assertEqual(result1[1],
                         datetime.strptime('2015-11-30 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

        # 2015-12-1
        result2 = MCDate.curr_month(self.day2)
        self.assertEqual(result2[0],
                         datetime.strptime('2015-12-1', '%Y-%m-%d'))
        self.assertEqual(result2[1],
                         datetime.strptime('2015-12-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

        # 2016-1-1
        result3 = MCDate.curr_month(self.day3)
        self.assertEqual(result3[0],
                         datetime.strptime('2016-1-1', '%Y-%m-%d'))
        self.assertEqual(result3[1],
                         datetime.strptime('2016-1-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

        # 2016-1-4
        result4 = MCDate.curr_month(self.day4)
        self.assertEqual(result4[0],
                         datetime.strptime('2016-1-1', '%Y-%m-%d'))
        self.assertEqual(result4[1],
                         datetime.strptime('2016-1-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

    def test_last_month(self):
        # 2015-11-23
        result1 = MCDate.last_month(self.day1)
        self.assertEqual(result1[0],
                         datetime.strptime('2015-10-1', '%Y-%m-%d'))
        self.assertEqual(result1[1],
                         datetime.strptime('2015-10-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

        # 2015-12-1
        result2 = MCDate.last_month(self.day2)
        self.assertEqual(result2[0],
                         datetime.strptime('2015-11-1', '%Y-%m-%d'))
        self.assertEqual(result2[1],
                         datetime.strptime('2015-11-30 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

        # 2016-1-1
        result3 = MCDate.last_month(self.day3)
        self.assertEqual(result3[0],
                         datetime.strptime('2015-12-1', '%Y-%m-%d'))
        self.assertEqual(result3[1],
                         datetime.strptime('2015-12-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

        # 2016-1-4
        result4 = MCDate.last_month(self.day4)
        self.assertEqual(result4[0],
                         datetime.strptime('2015-12-1', '%Y-%m-%d'))
        self.assertEqual(result4[1],
                         datetime.strptime('2015-12-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

    def test_curr_quarter(self):
        # 2015-11-23
        result1 = MCDate.curr_quarter(self.day1)
        self.assertEqual(result1[0],
                         datetime.strptime('2015-10-1', '%Y-%m-%d'))
        self.assertEqual(result1[1],
                         datetime.strptime('2015-12-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

        # 2015-12-1
        result2 = MCDate.curr_quarter(self.day2)
        self.assertEqual(result2[0],
                         datetime.strptime('2015-10-1', '%Y-%m-%d'))
        self.assertEqual(result2[1],
                         datetime.strptime('2015-12-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

        # 2016-1-1
        result3 = MCDate.curr_quarter(self.day3)
        self.assertEqual(result3[0],
                         datetime.strptime('2016-1-1', '%Y-%m-%d'))
        self.assertEqual(result3[1],
                         datetime.strptime('2016-3-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

        # 2016-1-4
        result4 = MCDate.curr_quarter(self.day4)
        self.assertEqual(result4[0],
                         datetime.strptime('2016-1-1', '%Y-%m-%d'))
        self.assertEqual(result4[1],
                         datetime.strptime('2016-3-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

    def test_last_quarter(self):
        # 2015-11-23
        result1 = MCDate.last_quarter(self.day1)
        self.assertEqual(result1[0],
                         datetime.strptime('2015-7-1', '%Y-%m-%d'))
        self.assertEqual(result1[1],
                         datetime.strptime('2015-9-30 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

        # 2015-12-1
        result2 = MCDate.last_quarter(self.day2)
        self.assertEqual(result2[0],
                         datetime.strptime('2015-7-1', '%Y-%m-%d'))
        self.assertEqual(result2[1],
                         datetime.strptime('2015-9-30 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

        # 2016-1-1
        result3 = MCDate.last_quarter(self.day3)
        self.assertEqual(result3[0],
                         datetime.strptime('2015-10-1', '%Y-%m-%d'))
        self.assertEqual(result3[1],
                         datetime.strptime('2015-12-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

        # 2016-1-4
        result4 = MCDate.last_quarter(self.day4)
        self.assertEqual(result4[0],
                         datetime.strptime('2015-10-1', '%Y-%m-%d'))
        self.assertEqual(result4[1],
                         datetime.strptime('2015-12-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

    def test_curr_year(self):
        # 2015-11-23
        result1 = MCDate.curr_year(self.day1)
        self.assertEqual(result1[0],
                         datetime.strptime('2015-1-1', '%Y-%m-%d'))
        self.assertEqual(result1[1],
                         datetime.strptime('2015-12-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

        # 2015-12-1
        result2 = MCDate.curr_year(self.day2)
        self.assertEqual(result2[0],
                         datetime.strptime('2015-1-1', '%Y-%m-%d'))
        self.assertEqual(result2[1],
                         datetime.strptime('2015-12-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

        # 2016-1-1
        result3 = MCDate.curr_year(self.day3)
        self.assertEqual(result3[0],
                         datetime.strptime('2016-1-1', '%Y-%m-%d'))
        self.assertEqual(result3[1],
                         datetime.strptime('2016-12-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

        # 2016-1-4
        result4 = MCDate.curr_year(self.day4)
        self.assertEqual(result4[0],
                         datetime.strptime('2016-1-1', '%Y-%m-%d'))
        self.assertEqual(result4[1],
                         datetime.strptime('2016-12-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

    def test_last_year(self):
        # 2015-11-23
        result1 = MCDate.last_year(self.day1)
        self.assertEqual(result1[0],
                         datetime.strptime('2014-1-1', '%Y-%m-%d'))
        self.assertEqual(result1[1],
                         datetime.strptime('2014-12-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

        # 2015-12-1
        result2 = MCDate.last_year(self.day2)
        self.assertEqual(result2[0],
                         datetime.strptime('2014-1-1', '%Y-%m-%d'))
        self.assertEqual(result2[1],
                         datetime.strptime('2014-12-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

        # 2016-1-1
        result3 = MCDate.last_year(self.day3)
        self.assertEqual(result3[0],
                         datetime.strptime('2015-1-1', '%Y-%m-%d'))
        self.assertEqual(result3[1],
                         datetime.strptime('2015-12-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))

        # 2016-1-4
        result4 = MCDate.last_year(self.day4)
        self.assertEqual(result4[0],
                         datetime.strptime('2015-1-1', '%Y-%m-%d'))
        self.assertEqual(result4[1],
                         datetime.strptime('2015-12-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))
