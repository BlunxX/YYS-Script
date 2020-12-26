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


class Chapter(Autogui):
    def __init__(self, win_name='阴阳师-网易游戏'):
        Autogui.__init__(self, win_name)
        # 设置当前副本的类型，设置之后优先查找御灵对应的截图
        self.screenshot.set_current_setion('chapter')  # 设置优先的截图信息
        self.config.set_current_setion('chapter')  # 设置当前配置信息
        self.pre_loop_times = self.config.cur_config.get('pre_loop_times', 20)
        self.loop_times = self.config.cur_config.get('loop_times', 20)
        self.captain = self.config.cur_config.get('captain', True)
        self.players = self.config.cur_config.get('players', 1)
        self.fodder_type = self.config.cur_config.get('fodder_type', 'fodder')
        self.drag = self.config.cur_config.get('drag', 5)  # 拖动距离
        self.cur_bad_loop_times = 0
        self.max_bad_loop_times = 20  # 卡在某个循环中的最大次数
        self.cur_monster_is_boss = False
        self.cur_loop_times = 0
        self.first_prepare_after_fight = True

        prepare_callback = [
            ('search', self.click_loc_one),
            # ('build_team', self.click_loc_one),   # 组队挑战暂不考虑自动邀请的问题
            # ('create_team', self.click_loc_one),
            # ('unpulic', self.click_loc_one),
        ]
        loop_callback = [
            ('chapter', self.click_loc_one),
            ('task_accept', self.task_accept_callback),
            ('enter_chapter', self.fight_callback),  # 单人挑战，可见即为单人
            ('team_fight', self.team_fight_callback),  # absent
            ('monster_fight', self.monster_fight_callback),
            ('boss_fight', self.boss_fight_callback),  # 组队挑战
            ('prepare', self.prepare_callback),
            ('chapter_award_detail', self.chapter_award_detail_callback),
            ('chapter_award_box', self.click_loc_one),
            ('award_box_after_chapter', self.click_loc_one),
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
        im_yys = self.screenshot_exact()
        self.cur_key = 'chapter_award_detail'
        loc_tmp = self.locate_im(self.get_image('empty_monster'), im_yys)
        if loc_tmp:
            self.click_loc_one(loc_tmp)
            return

    def team_fight_callback(self, loc):
        im_yys = self.screenshot_exact()
        loc_tmp = self.locate_im(self.get_image('team_fight'), im_yys)
        if loc_tmp:
            loc_absent = self.locate_im(self.get_image('absent'), im_yys)
            if self.captain is False or loc_absent:
                self.display_msg('等待队员来启后才能进入章节')
                self.check_bad_loop(self.cur_key)
                time.sleep(2)
                self.team_fight_callback(loc_tmp)
            else:
                self.click_loc_one(loc_tmp)

    def fight_callback(self, loc):
        self.first_prepare_after_fight = True
        self.click_loc_one(loc)

    def boss_fight_callback(self, loc):
        self.cur_monster_is_boss = True
        self.click_loc_one(loc)
        time.sleep(3)

    def monster_fight_callback(self, loc):
        im_yys = self.screenshot_exact()
        loc_tmp = self.locate_im(self.get_image('boss_fight'), im_yys)
        if loc_tmp:
            self.cur_key = 'boss_fight'
            self.click_loc_one(loc_tmp)
        else:
            self.click_loc_one(loc)
            time.sleep(3)

    def _preinstall_nees_change_fodder(self, man_nums):
        '''
                captain   players   至少多少只需要更换
        单人     True      1         2
        多人队长  True      2         1
        多人队员  False     2         2
        默认组队时，队员带狗粮队长
        '''
        if self.players == 1:
            if man_nums > 1:
                return True
        else:
            if self.captain and man_nums > 0:
                return True
            elif self.captain is False and man_nums > 1:
                return True
        return False

    def change_fodder_type(self, fodder_type: str):
        im_yys = self.screenshot_exact()
        loc_tmp = self.locate_im(self.get_image(fodder_type), im_yys)
        if loc_tmp:
            self.display_msg('已经是选中的狗粮类型')
            return

        all_types = ['all', 'fodder', 'ncard', 'srcard', 'ssrcard', 'spcard']
        all_types.remove(fodder_type)
        for each in all_types:
            loc_tmp = self.locate_im(self.get_image(each), im_yys)
            if loc_tmp:
                self.click_loc_one(loc_tmp)
                time.sleep(1)
                break

        im_yys = self.screenshot_exact()
        loc_tmp = self.locate_im(self.get_image(fodder_type), im_yys)
        if loc_tmp:
            self.click_loc_one(loc_tmp)
            self.display_msg('切换到选中的狗粮类型')

    def get_exchange_fodder_locations(self, locations):
        '''
            获取需要更换狗粮的式神式神位置
            0    式神1    loc_edge_x_1    式神2    loc_edge_x_2   式神3
        '''
        loc_edge_x_1 = 260
        loc_edge_x_2 = 530
        fodder_locs = []
        for loc in locations:
            if loc.left < loc_edge_x_1:
                fodder_locs.append(loc)
            elif loc.left < loc_edge_x_2:
                fodder_locs.append(loc)
        return fodder_locs

    def exchange_fodder(self, locations: list):
        if len(locations) == 0:
            self.display_msg('本次不需要更换狗粮')
            im_yys = self.screenshot_exact()
            loc_tmp = self.locate_im(self.get_image('prepare'), im_yys)
            if loc_tmp:
                self.cur_key = 'prepare'
                self.click_loc_one(loc_tmp)
            return

        # 拖动一定距离的待选狗粮，拖动到没有5星式神为止
        while True:
            im_yys = self.screenshot_exact()
            loc_red_egg = self.locate_im(self.get_image('red_egg'), im_yys)
            if loc_red_egg:
                # 还需要继续拖动
                loc_tmp = self.locate_im(self.get_image('move_button'), im_yys)
                if loc_tmp:
                    random_x = uniform(0.2 * loc_tmp.width,
                                       0.8 * loc_tmp.width)
                    random_y = uniform(0.2 * loc_tmp.height,
                                       0.8 * loc_tmp.height)
                    self.move_loc_inc(loc_tmp.left + random_x,
                                      loc_tmp.top + random_y)
                    self.dragRel_loc_exact(3, 0, 0.5)  # 每次向右拖动
            else:
                # 按配置额外再拖动距离
                if self.drag > 0:
                    loc_tmp = self.locate_im(self.get_image('move_button'),
                                             im_yys)
                    if loc_tmp:
                        random_x = uniform(0.2 * loc_tmp.width,
                                           0.8 * loc_tmp.width)
                        random_y = uniform(0.2 * loc_tmp.height,
                                           0.8 * loc_tmp.height)
                        self.move_loc_inc(loc_tmp.left + random_x,
                                          loc_tmp.top + random_y)
                        self.dragRel_loc_exact(3, 0, 0.5)  # 每次向右拖动
                break

        im_yys = self.screenshot_exact()
        flower_locs = self.get_all_images('flower', im_yys)
        if flower_locs:
            # flower_locs 数量一定是大于 locations 数量
            for i in range(len(locations)):
                start_x = flower_locs[i].left + uniform(
                    0.2 * flower_locs[i].width, 0.8 * flower_locs[i].width)
                start_y = flower_locs[i].top + uniform(
                    0.2 * flower_locs[i].height, 0.8 * flower_locs[i].height)

                self.move_loc_inc(start_x, start_y)
                self.dragRel_loc_exact(locations[i].left + 10 - start_x,
                                       locations[i].top + 20 - start_y, 1)

    def prepare_callback(self, loc):
        im_yys = self.screenshot_exact()
        locations = self.get_all_images('man', im_yys, 0.7)
        man_nums = len(locations) if locations else 0

        if man_nums == 0:
            self.click_loc_one(loc)
            return

        # 预设界面：刚进入挑战，含有预设的界面
        loc_tmp = self.locate_im(self.get_image('preinstall'), im_yys)
        if loc_tmp:
            if self._preinstall_nees_change_fodder(man_nums):
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
            if man_nums > 0 and man_nums < 4:
                self.cur_key = 'exchange_fodder'
                exchange_locs = self.get_exchange_fodder_locations(locations)
                self.exchange_fodder(exchange_locs)
                self.display_msg('狗粮替换完成')
            else:
                self.cur_key = 'change_fodder_type'
                self.change_fodder_type(self.fodder_type)
                self.prepare_callback(loc)

    def empty_monster_callback(self, loc):
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
    print(autogui.prepare_image_callback)
    print(autogui.loop_image_callback)
