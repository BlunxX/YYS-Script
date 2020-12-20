#!/usr/bin/python
# -*- coding: utf-8 -*

# %% 先加载对应的库
import configparser
import os
import sys

# %% 取出配置对应的文件
cur_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]
CONF_PATH = os.path.join(cur_dir, 'conf', 'config.ini')


class Config:
    def __new__(cls, *args, **kwargs):
        # 将一个类的实例绑定到类变量_instance上
        if not hasattr(cls, '_instrance'):
            # 构建父类，该父类的内存空间内最多允许相同名字子类的实例对象存在1个
            orig = super(Config, cls)
            cls._instrance = orig.__new__(cls)
        return cls._instrance

    def __init__(self, confpath=CONF_PATH):
        self.cur_config = None
        self.parser_created = False
        self.config_parser = configparser.RawConfigParser()
        try:
            self.config_parser.read(confpath, encoding='utf-8')
            self.parser_created = True
        except Exception as error:
            print('读取配置文件失败：{0},{1}'.format(confpath, str(error)))

    def is_parser_created(self):
        return self.parser_created

    def read_option_str(self, section, option, default):
        if self.parser_created is False:
            return default

        try:
            return self.config_parser.get(section, option)
        except Exception as error:
            print('获取{0},{1}失败, {2}'.format(section, option, str(error)))
            return default

    def read_option_int(self, section, option, default):
        if self.parser_created is False:
            return default

        try:
            return self.config_parser.getint(section, option)
        except Exception as error:
            print('获取{0},{1}失败, {2}'.format(section, option, str(error)))
            return default

    def read_option_bool(self, section, option, default):
        if self.parser_created is False:
            return default

        try:
            return self.config_parser.getboolean(section, option)
        except Exception as error:
            print('获取{0},{1}失败, {2}'.format(section, option, str(error)))
            return default

    def set_current_setion(self, section):
        self.cur_config = getattr(self, section)

    def read_one_type_config(self, read_type: str, read_keys: (str, str, str)):
        '''read_keys的三个位置分别代表： key, type, default_value'''

        if hasattr(self, read_type):
            print('{0}类型已经读取过一次了，请求检查配置文件并进行合并'.format(read_type))
            return
        else:
            sections = self.config_parser.sections()
            setattr(self, read_type, {})  # 新增一个字典
            config = getattr(self, read_type)
            if read_type not in sections:
                print('没有找到sections:{0}，使用默认值赋值'.format(read_type))
                for one_key in read_keys:
                    config[one_key[0]] = one_key[2]
                return
            else:
                for (key, type, default_value) in read_keys:
                    if type == 'int':
                        value = self.read_option_int(read_type, key,
                                                     default_value)
                        config[key] = value
                    elif type == 'str':
                        value = self.read_option_str(read_type, key,
                                                     default_value)
                        config[key] = value
                    elif type == 'bool':
                        value = self.read_option_bool(read_type, key,
                                                      default_value)
                        config[key] = value
                    else:
                        config[key] = default_value


class YysConfig(Config):
    def __init__(self, name, confpath=CONF_PATH):
        self.name = name
        Config.__init__(self, confpath)

    def get_configs_by_type(self, find_type: str) -> dict:
        if self.parser_created is False:
            return None

        if hasattr(self, find_type):
            return getattr(self, find_type)
        else:
            return None


yys_config = YysConfig(name='yys_config')
general_keys = [
    ('title', 'str', 'x笑cry-辅助工具'),
    ('version', 'str', 'v1.0.0'),
    ('gitpath', 'str', '无'),
]
yuling_keys = [
    ('loop_times', 'int', 200),
    ('type', 'str', 'dragon'),
    ('layer', 'int', 3),
    ('attention', 'str', ''),
]
yuhun_keys = [
    ('loop_times', 'int', 200),
    ('players', 'int', 2),
    ('may_fail', 'bool', True),
    ('captain', 'bool', True),
    ('attention', 'str', ''),
]

wangzhe_keys = [
    ('loop_times', 'int', 50),
    ('attention', 'str', ''),
]

yys_config.read_one_type_config('general', general_keys)
# print(getattr(yys_config, 'general'))
yys_config.read_one_type_config('yuling', yuling_keys)
# print(getattr(yys_config, 'yuling'))
yys_config.read_one_type_config('yuhun', yuhun_keys)
# print(getattr(yys_config, 'yuhun'))
yys_config.read_one_type_config('wangzhe', wangzhe_keys)
# print(getattr(yys_config, 'wangzhe'))

if __name__ == '__main__':
    yys_config = YysConfig(name='yys_config')
    print(yys_config.is_parser_created())

    general_keys = [
        ('title', 'str', 'x笑cry-辅助工具'),
        ('version', 'str', 'v1.0.0'),
        ('gitpath', 'str', '无'),
    ]
    yys_config.read_one_type_config('general', general_keys)
    print(getattr(yys_config, 'general'))
