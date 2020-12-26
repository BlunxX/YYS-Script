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


class Yuhun(Autogui):
    def __init__(self, win_name='阴阳师-网易游戏'):
        Autogui.__init__(self, win_name)
        # 设置当前副本的类型，设置之后优先查找御灵对应的截图
        self.screenshot.set_current_setion('yuhun')  # 设置优先的截图信息
        self.config.set_current_setion('yuhun')  # 设置当前配置信息
        self.pre_loop_times = self.config.cur_config.get('pre_loop_times', 20)
        self.loop_times = self.config.cur_config.get('loop_times', 20)
        self.captain = self.config.cur_config.get('captain', True)
        self.prepare_click_times = 0

        prepare_callback = [
            ('search', self.click_loc_one),
            ('yuhun', self.click_loc_one),
        ]
        loop_callback = [
            ('task_accept', self.task_accept_callback),
            ('always_accept', self.click_loc_one),
            ('accept', self.click_loc_one),
            ('fight', self.fight_callback),  # 单人挑战
            ('team_fight', self.team_fight_callback),  # 组队挑战
            ('confirm', self.click_loc_one),
            ('prepare', self.prepare_callback),
            ('victory', self.victory_callback),
            ('fail', self.fail_callback),
            ('award', self.award_callback),
        ]

        self.init_image_callback(prepare_callback, loop_callback)

    def prepare_callback(self, loc):
        if self.prepare_click_times < 3:
            self.click_loc_one_and_move_uncover(loc)
            self.prepare_click_times += 1
            time.sleep(1)
        self.click_success_check('prepare', self.prepare_callback)

    def fight_callback(self, loc):
        self.click_loc_one(loc)

    def team_fight_callback(self, loc):
        if self.captain:
            im_yys = self.screenshot_exact()
            locations = self.get_all_images('absent', im_yys)
            match_nums = len(locations) if locations else 0
            if (self.players == 2 and match_nums > 1) or (self.players == 3
                                                          and match_nums > 0):
                self.display_msg('队员还未来齐，需要等待队友来齐')
            else:
                self.click_loc_one(loc)
            time.sleep(1)


if __name__ == '__main__':
    autogui = Yuhun()
    autogui.run('yuhun')
    print(autogui.prepare_image_callback)
    print(autogui.loop_image_callback)
