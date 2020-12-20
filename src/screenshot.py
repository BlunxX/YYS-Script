#!/usr/bin/python
# -*- coding: utf-8 -*

# %% 先加载对应的库
import os
import sys
from PIL import Image

# %% 取出图片对应的截图文件，文件的目录结构
cur_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]
IMAGES_PATH = os.path.join(cur_dir, 'screenshot')
'''
图片类型1：
    图片1.jpg
    图片2.jpg
图片类型2：
    图片1.jpg
    图片2.jpg
'''


class Screenshot:
    def __init__(self, image_path=IMAGES_PATH):
        self.path = image_path
        self.path_exists = os.path.exists(IMAGES_PATH)
        self.cur_section = None

        if (self.path_exists):
            self.sections = [
                x for x in os.listdir(self.path)
                if os.path.isdir(os.path.join(self.path, x))
            ]

    def is_path_exists(self):
        return self.path_exists

    def open_image_file(self, image_path) -> Image:
        try:
            return Image.open(image_path)
        except Exception as error:
            print('打开图片失败，{0}, msg:{1}'.format(image_path, error))
            return None

    def read_section_jpg(self, section):
        if hasattr(self, section):
            print('find_all_jpg: already has section:{0}'.format(section))
            return False

        setattr(self, section, {})  # 添加对应的副本分类的字典
        new_attr = getattr(self, section)

        # 递归遍历目录及子目录下的所有文档 (root, ds, fs)
        dirpath = os.path.join(self.path, section)
        jpg_files = {}
        for each_walk in os.walk(dirpath):
            for file in each_walk[2]:
                if file.endswith('.jpg'):
                    jpg_files[file[:-4:]] = self.open_image_file(
                        os.path.join(each_walk[0], file))
        new_attr.update(jpg_files)
        return True

    def read_all_sections(self):
        for section in self.sections:
            self.read_section_jpg(section)

    def get_section_jpg(self, section, key):
        if hasattr(self, section):
            imags = getattr(self, section)
            if key in imags:
                return imags[key]

        imags = getattr(self, 'general')
        if key in imags:
            return imags[key]
        return None

    def set_current_setion(self, section: str):
        self.cur_section = section


class YysScreenshot(Screenshot):
    def __init__(self, section, image_path=IMAGES_PATH):
        Screenshot.__init__(self, image_path)
        self.read_all_sections()
        self.set_current_setion(section)

    def get_jpg(self, key):
        return self.get_section_jpg(self.cur_section, key)

    def get_jpgs(self, keys):
        images = {}
        for key in keys:
            images[key] = self.get_jpg(key)
        return images


yys_screenshot = YysScreenshot('')


if __name__ == '__main__':
    # screenshot = Screenshot()
    # if screenshot.is_path_exists():
    #     screenshot.read_section_jpg('yeyuanhuo')
    #     print(getattr(screenshot, 'yeyuanhuo'))

    #     screenshot.read_section_jpg('yuling')
    #     print(getattr(screenshot, 'yuling'))

    #     screenshot.read_section_jpg('general')
    #     print(getattr(screenshot, 'general'))

    #     screenshot.get_section_jpg('yeyuanhuo', 'absent').show()
    screenshot = YysScreenshot('yeyuanhuo')
    jpgs = screenshot.get_jpgs(['absent', 'chi'])
    images = [x[1] for x in jpgs.items()]
    print(None in images)
