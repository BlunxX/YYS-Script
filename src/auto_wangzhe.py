#!/usr/bin/python
# -*- coding: utf-8 -*

# %% 先加载对应的库, x_top(383,229) x_bottom(1474,846) w_h(1090,617)
import os
import sys
import time
from random import randint, uniform

cur_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]
sys.path.append(os.path.join(cur_dir, 'autogui'))

from autogui import Autogui, ImageCallback


class Wangzhe(Autogui):
    def __init__(self, win_name='腾讯手游助手【极速傲引擎-7.1】'):
    # def __init__(self, win_name='王者荣耀 - MuMu模拟器'):
        Autogui.__init__(self, win_name)
        # 设置当前副本的类型，设置之后优先查找御灵对应的截图
        self.screenshot.set_current_setion('wangzhe')  # 设置优先的截图信息
        self.config.set_current_setion('wangzhe')  # 设置当前配置信息
        self.pre_loop_times = self.config.cur_config.get('pre_loop_times', 20)
        self.loop_times = self.config.cur_config.get('loop_times', 20)
        self.already_auto = False  # 已经点击自动
        self.cur_loop_times = 0

        prepare_callback = [
            ('wangxiangtiangong', self.click_loc_one_and_move_uncover),
            ('maoxianwangfa', self.click_loc_one_and_move_uncover),
            ('duoluo_fight', self.click_loc_one_and_move_uncover),
            ('next', self.next_callback),  # +下一步，王者，大师，下一章
        ]
        loop_callback = [
            ('fight', self.click_loc_one_and_move_uncover),
            ('loding', self.void_callback),
            ('skip', self.click_loc_one_and_move_uncover),
            ('skip2', self.click_loc_one_and_move_uncover),
            ('waiting', self.void_callback),
            ('continue', self.click_loc_one_and_move_uncover),
            ('fight_again', self.fight_again_callback),  # +金币上限
            ('auto', self.void_callback),
        ]

        self.init_image_callback(prepare_callback, loop_callback)

    def next_callback(self, loc):
        '''血红色王者宫殿'''
        loc_tmp = self.locate_im(self.get_image('wanggong'))
        if loc_tmp:
            self.click_loc_one_and_move_uncover(loc_tmp)

            time.sleep(0.5)
            loc_tmp = self.locate_im(self.get_image('dashi_unclicked'))
            if loc_tmp:
                self.cur_key = 'dashi_unclicked'
                self.click_loc_one_and_move_uncover(loc_tmp)
                time.sleep(0.5)
                self.click_success_check('award', self.next_callback)
            else:
                self.click_loc_one_and_move_uncover(loc)  # 点击下一步
        else:
            loc_tmp = self.locate_im(self.get_image('next_chapter'))
            if loc_tmp:
                self.cur_key = 'next_chapter'
                self.click_loc_one_and_move_uncover(loc_tmp)
                time.sleep(0.5)
                self.click_success_check('award', self.next_callback)

    def fight_again_callback(self, loc):
        self.cur_loop_times += 1
        self.display_msg('已完成：{0}/{1}'.format(self.cur_loop_times,
                                              self.loop_times))
        loc_tmp = self.locate_im(self.get_image('money_limited'))
        if loc_tmp:
            self.display_msg('本周收益已达上限，正在退出')
            self.stop = True
        else:
            self.click_loc_one_and_move_uncover(loc)  # 点击下一步

    def click_loc_one_and_move_uncover(self, loc):
        self.click_loc_one(loc)
        self.move_uncover_to_right(loc)
        time.sleep(0.8)

    def run(self, auto_type: str):
        # 腾讯手游助手不能自动调整大小： 453 308 936 584
        self.auto_type = auto_type
        if self.get_window_handler() is False:
            self.display_msg('获取窗体大小失败')
            return
        self.display_msg('正在尝试进入循环')
        if self.goto_loop() is False:
            self.display_msg('无法进入循环')
            return
        self.display_msg('成功进入循环脚本')
        self.display_msg(str(self.config.cur_config))  # 打印配置信息
        self.loop()


if __name__ == '__main__':
    autogui = Wangzhe()
    autogui.run('wangzhe')
    print(autogui.prepare_image_callback)
    print(autogui.loop_image_callback)
