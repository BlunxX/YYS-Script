#!/usr/bin/python
# -*- coding: utf-8 -*

# %% 先加载对应的库
import os
import sys
import time
import logging
from random import randint, uniform

cur_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]
sys.path.append(os.path.join(cur_dir, 'autogui'))
logger = logging.getLogger('kiddo')

from autogui import Autogui, ImageCallback


class Chapter(Autogui):
    def __init__(self, win_name='阴阳师-网易游戏'):
        Autogui.__init__(self, win_name)
        # 设置当前副本的类型，设置之后优先查找御灵对应的截图
        self.screenshot.set_current_setion('chapter')  # 设置优先的截图信息
        self.config.set_current_setion('chapter')  # 设置当前配置信息
        self.pre_loop_times = self.config.cur_config.get('pre_loop_times', 20)
        self.loop_times = self.config.cur_config.get('loop_times', 20)
        self.is_captain = self.config.cur_config.get('captain', True)
        self.players = self.config.cur_config.get('players', 2)
        if self.is_captain is False and self.players == 1:
            self.is_captain = True
        self.is_member = True if (self.is_captain is False
                                  and self.players > 1) else False
        self.fodder_type = self.config.cur_config.get('fodder_type', 'fodder')
        self.drag = self.config.cur_config.get('drag', 3)  # 拖动距离
        self.cur_monster_is_boss = False
        self.cur_loop_times = 0

        self.captain_preinstall_locs = [[270, 185, 100, 170],
                                        [420, 240, 110, 170]]
        self.captain_exchange_locs = [[0, 111, 265, 195], [265, 110, 265, 195]]
        self.captain_team_preinstall_locs = [[0, 200, 120, 200],
                                             [300, 355, 120, 170]]
        self.captain_team_exchange_locs = [[173, 146, 100, 159],
                                           [524, 146, 100, 159]]

        prepare_callback = [
            ('search', self.click_loc_one_and_move_uncover),
            # ('build_team', self.click_loc_one_and_move_uncover),   # 组队挑战暂不考虑自动邀请的问题
            # ('create_team', self.click_loc_one_and_move_uncover),
            # ('unpublished', self.click_loc_one_and_move_uncover),
        ]
        loop_callback = [
            ('award_box_after_chapter', self.click_loc_one_and_move_uncover),
            ('yes', self.click_loc_one_and_move_uncover),  # 确认继续邀请
            ('accept', self.click_loc_one_and_move_uncover),  # 确认接受邀请
            ('chapter', self.chapter_callback),  # 队员不用点
            ('task_accept', self.task_accept_callback),
            ('enter_chapter', self.fight_callback),  # 单人挑战，可见即为单人
            ('team_fight', self.team_fight_callback),  # absent
            ('monster_fight', self.monster_fight_callback),
            ('boss_fight', self.boss_fight_callback),  # 组队挑战
            ('prepare', self.prepare_callback),
            ('chapter_award_detail', self.chapter_award_detail_callback),
            ('chapter_award_box', self.click_loc_one_and_move_uncover),
            ('empty_monster', self.empty_monster_callback),  # 空怪物列表
            ('victory', self.victory_callback),
            ('fail', self.fail_callback),
            ('award', self.award_callback),
        ]

        self.init_image_callback(prepare_callback, loop_callback)

    def victory_callback(self, loc):
        self.display_msg('当前进度：{0}/{1}'.format(self.cur_loop_times + 1,
                                               self.loop_times))
        self.click_loc_one_when_award()
        time.sleep(1)
        if self.cur_monster_is_boss:
            self.cur_loop_times += 1
            self.cur_monster_is_boss = False
        self.click_success_check('victory', self.victory_callback)

    def chapter_award_detail_callback(self, loc):
        '''没有找到任务怪物'''
        im_yys = self.screenshot_exact()
        self.cur_key = 'chapter_award_detail'
        loc_tmp = self.locate_im(self.get_image('empty_monster'), im_yys)
        if loc_tmp:
            self.click_loc_one_and_move_uncover(loc_tmp)
            return

    def team_fight_callback(self, loc):
        im_yys = self.screenshot_exact()
        loc_tmp = self.locate_im(self.get_image('team_fight'), im_yys)
        if loc_tmp:
            loc_absent = self.locate_im(self.get_image('absent'), im_yys)
            if self.is_captain is False or loc_absent:
                self.display_msg('等待队员来启后才能进入章节')
                time.sleep(2)
                self.team_fight_callback(loc_tmp)
            else:
                self.click_loc_one_and_move_uncover(loc_tmp)

    def chapter_callback(self, loc):
        if self.is_member:
            return
        self.click_loc_one_and_move_uncover(loc)

    def fight_callback(self, loc):
        if self.is_member:
            return
        self.click_loc_one_and_move_uncover(loc)

    def boss_fight_callback(self, loc):
        self.cur_monster_is_boss = True
        if self.is_member:
            return
        self.click_loc_one_and_move_uncover(loc)
        wait_times = 2 if self.players == 1 else 4
        time.sleep(wait_times)

    def monster_fight_callback(self, loc):
        if self.is_member:
            return
        im_yys = self.screenshot_exact()
        loc_tmp = self.locate_im(self.get_image('boss_fight'), im_yys)
        if loc_tmp:
            self.cur_key = 'boss_fight'
            self.click_loc_one_and_move_uncover(loc_tmp)
        else:
            self.cur_key = 'monster_fight'
            self.click_loc_one_and_move_uncover(loc)
            wait_times = 2 if self.players == 1 else 4
            time.sleep(wait_times)

    def prepare_callback(self, loc):
        if self.is_captain:
            # 组队时，队长的位置信息会变化
            if self.players == 1:
                self.preinstall_locs = self.captain_preinstall_locs
                self.exchange_locs = self.captain_exchange_locs
            else:
                self.preinstall_locs = self.captain_team_preinstall_locs
                self.exchange_locs = self.captain_team_exchange_locs
        else:
            # 队员用的是单人组队时队长的位置信息
            self.preinstall_locs = self.captain_preinstall_locs
            self.exchange_locs = self.captain_exchange_locs

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
                self.click_loc_one_and_move_uncover(loc)
            return

        # 交换式神界面
        need_change_fodder = False
        if self.is_captain:
            if self.locate_im(self.get_image('exchange'), im_yys):
                need_change_fodder = True
        else:
            if self.locate_im(self.get_image('all'), im_yys) or self.locate_im(
                    self.get_image('fodder'), im_yys):
                need_change_fodder = True
        if need_change_fodder:
            locations = self.get_all_images_by_locs('man', self.exchange_locs)
            man_nums = len(locations)
            if man_nums > 0:
                self.cur_key = 'change_fodder_type'
                self.change_fodder_type(self.fodder_type)
                self.cur_key = 'exchange_fodder'
                self.exchange_fodder(locations, self.drag)
                self.display_msg('狗粮替换完成')
            else:
                self.cur_key = 'prepare'
                self.click_loc_one_and_move_uncover(loc)

    def empty_monster_callback(self, loc):
        if self.is_member:
            return
        random_x = uniform(0.2 * self.window.win_width,
                           0.4 * self.window.win_width)
        random_y = uniform(0.4 * self.window.win_height,
                           0.6 * self.window.win_height)
        self.move_loc_inc(random_x, random_y)
        self.dragRel_loc_exact(-250, 0, 0.5)  # 每次向右拖动
        self.display_msg('拖动一段距离来识别新的小怪')


if __name__ == '__main__':
    autogui = Chapter()
    autogui.run('chapter')
    logger.debug(str(autogui.prepare_image_callback))
    logger.debug(str(autogui.loop_image_callback))
