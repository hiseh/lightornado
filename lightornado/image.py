from enum import Enum
from os import path, makedirs
from re import compile
from unittest import TestCase

from PIL import Image
from requests import get, HTTPError

from app.baseconfig import BaseConfig
from lightornado.utils import mcmd5

__author__ = 'hisehyin'
__datetime__ = '16/1/19 下午1:37'


class ImageFormats(Enum):
    jpg = 'JPEG'
    jpeg = 'JPEG'
    png = 'PNG'


class MCImage:
    def __init__(self, local_path=None, url=None):
        """
        init image object
        :param local_path:local path
        :param url:remote path
        :return:
        """
        def parse_path(image_path):
            """
            解析路径
            :param image_path:
            :return:
            """
            image_match = compile(r"^(image/)|^(avatar/)|^(active/)")
            match_match = compile(r"^(match/)")
            lottery_match = compile(r"^(lottery/)")
            if image_match.match(image_path):
                real_path = ("./{php_path}/{image_path}"
                             .format(php_path=BaseConfig.php_path,
                                     image_path=image_path))
            elif match_match.match(image_path):
                real_path = ("./{MATCH_STORATE_PATH}/{image_path}"
                             .format(MATCH_STORATE_PATH=BaseConfig.match_path,
                                     image_path=image_path))
            elif lottery_match.match(image_path):
                real_path = ("{PREFIX_ABS_PATH}/{LOTTERY_STORAGE_PATH}/{image_path}"
                             .format(PREFIX_ABS_PATH=BaseConfig.tmp_path,
                                     LOTTERY_STORAGE_PATH=BaseConfig.lottery_path,
                                     image_path=image_path.replace("lottery/", "")))
            else:
                real_path = ("./{temp_path}/{image_path}"
                             .format(temp_path=BaseConfig.tmp_path,
                                     image_path=image_path))
            return real_path

        if url:
            try:
                self.image = Image.open(get(url, stream=True).raw)
                self.pwd = url
                self.ext = self.image.format
                self.islocal = False
            except (HTTPError, ValueError, OSError):
                self.pwd = "./tmp/icon.jpg"
                self.ext = ImageFormats.jpg
                self.image = Image.open(self.pwd)
                self.islocal = True
        else:
            try:
                self.pwd = parse_path(local_path)
                self.ext = ImageFormats[path.splitext(local_path)[1][1:]]
                self.image = Image.open(self.pwd)
                self.islocal = True
            except (FileNotFoundError, TypeError, KeyError, OSError):
                if "avatar" in self.pwd:
                    self.pwd = "./tmp/user.jpg"
                else:
                    self.pwd = "./tmp/icon.jpg"
                self.ext = ImageFormats.jpg
                self.image = Image.open(self.pwd)
                self.islocal = True

    def gen_cached_path(self, width, height, original_x=None, original_y=None, watermark=None):
        """
        generate cached path
        :param width:
        :param height:
        :param original_x:
        :param original_y:
        :param watermark:
        :return:
        """
        original_path = self.pwd + "_" + str(width) + "_" + str(height)

        if isinstance(original_x, int) and isinstance(original_y, int):
            original_path += "_" + str(original_x) + "_" + str(original_y)

        if isinstance(watermark, str):
            original_path += "_" + watermark

        md5_path = mcmd5(original_path)
        cached_path = ("./{tmp}/{pre1}/{pre2}/{pre3}"
                       .format(tmp=BaseConfig.tmp_path,
                               pre1=md5_path[:2],
                               pre2=md5_path[2:4],
                               pre3=md5_path[4:6]))
        if not path.isdir(cached_path):
            makedirs(cached_path)

        try:
            cached_path += "/" + md5_path + '.' + self.ext.name
        except AttributeError:
            self.ext = ImageFormats.jpg
            cached_path += "/" + md5_path + '.' + self.ext.name

        return cached_path

    def is_modified(self, aim_file):
        """
        siehls
        :param aim_file:
        :return:
        """
        try:
            return not (self.islocal and (path.getmtime(self.pwd) < path.getmtime(aim_file)))
        except FileNotFoundError:
            return True

    def thumb(self, width, height, watermark=None):
        """
        thumbnail image
        :param width:aim width
        :param height:aim height
        :param watermark:
        :return:
        """
        aim_file = self.gen_cached_path(width=width, height=height, watermark=watermark)
        if self.is_modified(aim_file=aim_file):
            size = width, height
            self.image.thumbnail(size=size)
            self.image.save(aim_file, self.ext.value)
            if watermark:
                self.add_watermark(watermark)

        self.close()
        return aim_file.replace("./tmp/", "")

    def crop(self, width, height, original_x=0, original_y=0, watermark=None):
        """
        crop image
        :param width: aim width
        :param height: aim hegith
        :param original_x:original x
        :param original_y:original y
        :param watermark:
        :return:
        """
        aim_file = self.gen_cached_path(width=width,
                                        height=height,
                                        original_x=original_x,
                                        original_y=original_y,
                                        watermark=watermark)
        if self.is_modified(aim_file=aim_file):
            (self.image.crop((original_x, original_y, width + original_y, height + original_y))
             .save(aim_file, self.ext.value))
            if watermark:
                self.add_watermark(watermark=watermark)

        self.close()
        return aim_file.replace("./tmp/", "")

    def add_watermark(self, watermark):
        """
        not working
        :param watermark:
        :return:
        """
        print(self.pwd, "watermark", watermark)
        pass

    def close(self):
        self.image.close()


'''
unit test
'''


class Test(TestCase):
    def setUp(self):
        self.original_image1 = MCImage(local_path="/Users/hisehyin/temp/1.jpg")
        self.original_image2 = MCImage(local_path="/Users/hisehyin/temp/2.png")

    def tearDown(self):
        self.original_image1.close()
        self.original_image2.close()

    def test_thumb(self):
        print(path.splitext('/Users/hisehyin/temp/2.png'))

    def test_crop(self):
        crop = self.original_image2.crop(width=10, height=10, original_x=0, original_y=0)
        crop_image = MCImage(local_path=crop)
        self.assertEqual(crop_image.image.size, (10, 10), msg="crop image")
        crop_image.close()
