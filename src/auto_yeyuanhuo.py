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


class Yeyuanhuo(Autogui):
    def __init__(self, win_name='阴阳师-网易游戏'):
        Autogui.__init__(self, win_name)
        # 设置当前副本的类型，设置之后优先查找御灵对应的截图
        self.screenshot.set_current_setion('yeyuanhuo')  # 设置优先的截图信息
        self.config.set_current_setion('yeyuanhuo')  # 设置当前配置信息
        self.pre_loop_times = self.config.cur_config.get('pre_loop_times', 20)
        self.loop_times = self.config.cur_config.get('loop_times', 20)
        self.change_fodder = self.config.cur_config.get('change_fodder', True)
        self.fodder_type = self.config.cur_config.get('fodder_type', 'fodder')
        self.drag = self.config.cur_config.get('drag', 5)  # 拖动距离
        self.exchange_locs = [[0, 110, 130, 200], [130, 110, 174, 200],
                              [304, 110, 176, 200]]
        self.preinstall_locs = [[310, 220, 133, 200], [447, 220, 133, 200],
                                [577, 220, 133, 200]]
        self.already_select_chi = False

        prepare_callback = [
            ('search', self.click_loc_one),
            ('yuhun', self.click_loc_one),  # 组队挑战暂不考虑自动邀请的问题
            ('yeyuanhuo', self.click_loc_one),
        ]
        loop_callback = [
            ('yeyuanhuo', self.click_loc_one),
            ('task_accept', self.task_accept_callback),
            ('fight', self.fight_callback),
            ('prepare', self.prepare_callback),
            ('victory', self.victory_callback),
            ('fail', self.fail_callback),
            ('award', self.award_callback),
            ('time', self.void_callback),
        ]

        self.init_image_callback(prepare_callback, loop_callback)

    def fight_callback(self, loc):
        if self.already_select_chi:
            self.click_loc_one(loc)
            return

        loc_tmp = self.locate_im(self.get_image('chi'))
        if loc_tmp:
            self.cur_key = 'chi'
            self.already_select_chi = True
            self.click_loc_one(loc_tmp)
            time.sleep(0.5)
        self.cur_key = 'fight'
        self.click_loc_one(loc)

    def prepare_callback(self, loc):
        if self.change_fodder is False:
            self.click_loc_one(loc)
            return

        # 预设界面：刚进入挑战，含有预设的界面
        im_yys = self.screenshot_exact()
        loc_tmp = self.locate_im(self.get_image('preinstall'), im_yys)
        if loc_tmp:
            locations = self.get_all_images_by_locs('man',
                                                    self.preinstall_locs)
            man_nums = len(locations) if locations else 0
            if man_nums > 0:
                random_x = uniform(-10, 10)
                random_y = uniform(-10, 10)
                self.cur_key = 'exchange_preinstall'
                self.click_loc_inc(350 + random_x, 320 + random_y, 1)
            else:
                self.display_msg('当前不需要更换狗粮')
                self.click_loc_one(loc)
                time.sleep(1)  # 避免太过频繁去点击准备
            return

        # 交换式神界面
        loc_tmp = self.locate_im(self.get_image('exchange'), im_yys)
        if loc_tmp:
            locations = self.get_all_images_by_locs('man', self.exchange_locs)
            man_nums = len(locations)
            if man_nums > 0:
                self.cur_key = 'change_fodder_type'
                self.change_fodder_type(self.fodder_type)
                self.cur_key = 'exchange_fodder'
                self.exchange_fodder(locations, self.drag)
                self.display_msg('狗粮替换完成')
            else:
                self.click_loc_one(loc)


if __name__ == '__main__':
    autogui = Yeyuanhuo()
    autogui.run('yeyuanhuo')
    print(autogui.prepare_image_callback)
    print(autogui.loop_image_callback)