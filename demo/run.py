from concurrent.futures import ProcessPoolExecutor
from os import path, walk
from lightornado.utils import shutdown_process
from sys import argv

from tornado import util
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.web import Application

from lightornado.globals_config import OptionType

__author__ = 'hisehyin'
__datetime__ = '16/1/13 下午8:34'


def __start_app(local_app):
    """
    启动一个app
    :param local_app
    :return:
    """
    app = getattr(__import__('app.{basename}'.format(basename=path.basename(local_app)),
                             fromlist=['config']),
                  'config').App
    handlers = []
    for handler in app.handlers:
        handlers.append((handler['url'], util.import_object(handler['handler'])))

    define('log_file_prefix', default=app.log_file, type=str, help='')
    options.parse_command_line()
    application = Application(handlers, **app.settings)
    http_server = HTTPServer(application)
    http_server.bind(app.port)
    http_server.start(app.process_count)
    IOLoop.instance().start()


def main(base_path):
    """
    查找app下所有应用,读取配置
    :param base_path 应用路径
    :return:
    """
    app_list = [app_path for app_path, _, _ in walk(base_path) if path.isfile(app_path + '/config.py')]
    with ProcessPoolExecutor(max_workers=len(app_list)) as executor:
        for app_path in app_list:
            executor.submit(__start_app, app_path)


if __name__ == '__main__':
    args = set(argv[1:])
    if '-h' in args:
        print('python run.py [debug] [option]\n'
              'debug\t: 是否进入调试模式.默认不进入\n'
              'option\t: 动作.默认是stop\n'
              '\tstart\t: 启动\n'
              '\tstop\t: 停止\n'
              '\trestart\t: 重启')
    else:
        debug = 1 if 'debug' in args else 0
        define('debug', default=debug, type=int, help='debug type')

        option = OptionType(1 if 'start' in args else 3 if 'restart' in args else 2)
        define('option', default=option.value, type=int, help='option type')

        try:
            app_base_path = argv[1]
            if not path.isdir(app_base_path):
                raise IndexError
        except IndexError:
            app_base_path = './app'

        define('app_base_path', default=app_base_path, type=str, help='app path')

        if option == OptionType.start:
            main(app_base_path)
        else:
            shutdown_process(path.basename(__file__))
