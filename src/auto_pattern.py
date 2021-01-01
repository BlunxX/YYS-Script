#!/usr/bin/python
# -*- coding: utf-8 -*

# %% 先加载对应的库
import os
import sys
import time
from random import randint, uniform

cur_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]
sys.path.append(os.path.join(cur_dir, 'autogui'))

from autogui import Autogui, ImageCallback


class Pattern(Autogui):
    def __init__(self, win_name='None'):
        Autogui.__init__(self, win_name)
        # 设置当前副本的类型，设置之后优先查找御灵对应的截图
        self.screenshot.set_current_setion('pattern')  # 设置优先的截图信息
        self.config.set_current_setion('pattern')  # 设置当前配置信息
        self.pre_loop_times = self.config.cur_config.get('pre_loop_times', 20)
        self.loop_times = self.config.cur_config.get('loop_times', 20)
        loop_keys = self.config.cur_config.get('loop_keys', '')
        prepare_keys = self.config.cur_config.get('prepare_keys', '')
        if loop_keys == '':
            self.display_msg('正在退出，请先设置loop_keys')
            self.stop = True
            return
        self.loop_keys = []
        self.prepare_keys = []

        tmp_keys = prepare_keys.split(',')
        for key in tmp_keys:
            if key == '':
                continue
            self.prepare_keys.append(key.strip())
        tmp_keys = loop_keys.split(',')
        for key in tmp_keys:
            if key == '':
                continue
            self.loop_keys.append(key.strip())
        # prepare_callback = [
        #     ('search', self.click_loc_one),
        # ]
        # loop_callback = [
        #     ('victory', self.victory_callback),
        #     ('fail', self.fail_callback),
        #     ('award', self.award_callback),
        # ]
        tmp_generator = zip(self.prepare_keys,
                            [self.click_loc_one_and_move_uncover] *
                            len(self.prepare_keys))
        prepare_callback = [x for x in tmp_generator]
        tmp_generator = zip(self.loop_keys,
                            [self.click_loc_one_and_move_uncover] *
                            len(self.loop_keys))
        loop_callback = [x for x in tmp_generator]
        self.init_image_callback(prepare_callback, loop_callback)

    def click_loc_one_and_move_uncover(self, loc):
        self.click_loc_one(loc)
        self.move_uncover_to_right(loc)
        time.sleep(0.8)


if __name__ == '__main__':
    autogui = Pattern()
    autogui.window.set_only_getwin(True)
    autogui.run('pattern')
    print(autogui.prepare_image_callback)
    print(autogui.loop_image_callback)
