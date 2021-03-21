'''
Author: caiyx
Date: 2020-12-28 21:48:25
LastEditTime: 2020-12-31 22:07:13
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: \new_yysscript\src\auto_yuhun.py
'''
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
        self.players = self.config.cur_config.get('players', 2)
        self.prepare_click_times = 0

        prepare_callback = [
            ('search', self.click_loc_one),
            ('yuhun', self.click_loc_one),
        ]
        loop_callback = [
            ('task_accept', self.task_accept_callback),
            ('always_accept', self.always_accept_callback),
            ('accept', self.accept_callback),  # 队员默认接受邀请
            ('fight', self.fight_callback),  # 单人挑战
            ('team_fight', self.team_fight_callback),  # 组队挑战
            ('time', self.void_callback),
            ('yes', self.yes_callback),  # 确认，队长默认邀请队员
            ('confirm', self.click_loc_one),  # 确定
            ('prepare', self.prepare_callback),
            ('victory', self.victory_callback),
            ('fail', self.fail_callback),
            ('award', self.award_callback),
        ]

        self.init_image_callback(prepare_callback, loop_callback)

    def prepare_callback(self, loc):
        if self.prepare_click_times < 4:
            self.click_loc_one_and_move_uncover(loc)
            self.prepare_click_times += 1
            time.sleep(1)
        self.click_success_check('prepare', self.prepare_callback)

    def always_accept_callback(self, loc):
        self.prepare_click_times = 10  # 默认邀请之后不需要重新点击准备
        self.cur_key = 'always_accept'
        self.click_loc_one(loc)

    def accept_callback(self, loc):
        self.prepare_click_times = 0  # 重新归零，需要点击准备
        self.cur_key = 'accept'
        self.click_loc_one(loc)

    def fight_callback(self, loc):
        self.click_loc_one(loc)

    def team_fight_callback(self, loc):
        need_wait_player = False
        if self.captain:
            im_yys = self.screenshot_exact()
            if self.players == 2:
                im_absent = self.screenshot_inc(320, 80, 150, 200)
                if self.locate_im(self.get_image('absent'), im_absent):
                    need_wait_player = True
            elif self.players == 3 and self.locate_im(self.get_image('absent'),
                                                      im_yys):
                need_wait_player = True

            if need_wait_player:
                self.display_msg('队员还未来齐，需要等待队友来齐')
            else:
                self.click_loc_one(loc)
            time.sleep(1)

    def yes_callback(self, loc):
        loc_tmp = self.locate_im(self.get_image('default_invite'))
        if loc_tmp:
            self.display_msg('设置为默认邀请队友')
            self.cur_key = 'default_invite'
            self.click_loc_inc(loc_tmp.left - 20, loc_tmp.top + 9, 1)
            self.cur_key = 'yes'
            time.sleep(0.5)
            self.click_loc_one(loc)


if __name__ == '__main__':
    autogui = Yuhun()
    autogui.run('yuhun')
    logger.debug(str(autogui.prepare_image_callback))
    logger.debug(str(autogui.loop_image_callback))
