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


class Yuling(Autogui):
    def __init__(self, win_name='阴阳师-网易游戏'):
        Autogui.__init__(self, win_name)
        # 设置当前副本的类型，设置之后优先查找御灵对应的截图
        self.screenshot.set_current_setion('yuling')  # 设置优先的截图信息
        self.config.set_current_setion('yuling')  # 设置当前配置信息
        self.pre_loop_times = self.config.cur_config.get('pre_loop_times', 20)
        self.loop_times = self.config.cur_config.get('loop_times', 20)
        self.fight_type = self.config.cur_config.get('type', 'leopard')
        self.already_select_layer = False

        prepare_callback = [
            ('search', self.click_loc_one),
            ('yuling', self.click_loc_one),
            ('dragon', self.dragon_callback),
            ('fox', self.fox_callback),
            ('leopard', self.leopard_callback),
            ('phenix', self.phenix_callback),
        ]
        loop_callback = [
            ('reward_accept', self.click_loc_one),
            ('fight', self.fight_callback),
            ('prepare', self.prepare_callback),
            ('victory', self.victory_callback),
            ('fail', self.fail_callback),
            ('award', self.award_callback),
        ]

        self.init_image_callback(prepare_callback, loop_callback)

    def _fighttype_callback(self, loc, fight_type):
        '''点击神龙'''
        if self.fight_type != fight_type:
            self.display_msg('挑战类型不匹配：{0}!={1}，切换到类型：{1}'.format(
                fight_type, self.fight_type))

        im_yys = self.screenshot_exact()
        loc_tmp = self.locate_im(self.get_image(self.fight_type), im_yys)
        if loc_tmp:
            self.cur_key = self.fight_type
            self.click_loc_one(loc_tmp)
        else:
            self.display_msg('无法切换到类型：{0}'.format(self.fight_type))
            return

    def dragon_callback(self, loc):
        self._fighttype_callback(loc, 'dragon')

    def fox_callback(self, loc):
        self._fighttype_callback(loc, 'fox')

    def leopard_callback(self, loc):
        self._fighttype_callback(loc, 'leopard')

    def phenix_callback(self, loc):
        self._fighttype_callback(loc, 'phenix')

    def fight_callback(self, loc):
        if self.already_select_layer is False:
            random_dis = randint(-10, 10)
            last_x = self.window.x_top + 280 + random_dis
            last_y = self.window.y_top + 500 + random_dis
            self.click_loc_exact(last_x, last_y, 2, 0.2)  # 点击两下显示更快
            self.already_select_layer = True
        else:
            self.click_loc_one_and_move_uncover(loc)


if __name__ == '__main__':
    autogui = Yuling()
    autogui.run('yuling')
    print(autogui.prepare_image_callback)
    print(autogui.loop_image_callback)
