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


class YysBreak(Autogui):
    def __init__(self, win_name='阴阳师-网易游戏'):
        Autogui.__init__(self, win_name)
        # 设置当前副本的类型，设置之后优先查找御灵对应的截图
        self.screenshot.set_current_setion('yys_break')  # 设置优先的截图信息
        self.config.set_current_setion('yys_break')  # 设置当前配置信息
        self.pre_loop_times = self.config.cur_config.get('pre_loop_times', 20)
        self.loop_times = self.config.cur_config.get('loop_times', 40)
        self.cur_type = 'group'
        self.group_done = False
        self.person_done = False
        self.person_inc_boxes = [  # 个人挑战的框体
            [100, 120, 205, 85],
            [305, 120, 205, 85],
            [505, 120, 205, 85],
            [100, 205, 205, 85],
            [305, 205, 205, 85],
            [505, 205, 205, 85],
            [100, 290, 205, 85],
            [305, 290, 205, 85],
            [505, 290, 205, 85],
        ]
        self.group_inc_boxes = [  # 寮挑战的框体
            [270, 115, 205, 85],
            [470, 115, 205, 85],
            [270, 200, 205, 85],
            [470, 200, 205, 85],
            [270, 285, 205, 85],
            [470, 285, 205, 85],
            [270, 365, 205, 85],
            [470, 365, 205, 85],
        ]
        self.four_role_inc_box = [450, 125, 125, 250]
        self.four_click_inc_pos = (510, 280)

        prepare_callback = [
            ('search', self.click_loc_one),
            ('break', self.click_loc_one),
        ]
        loop_callback = [
            ('task_accept', self.task_accept_callback),
            ('refresh', self.person_callback),  # 个人挑战
            ('group', self.group_callback),  # 寮挑战
            ('continue', self.click_loc_one_and_move_uncover),  # 3,6,9时用到
            ('prepare', self.prepare_callback),  # 负责后续打标记
            ('unselected', self.unselected_callback),  # 早上太早，会长还未选择对抗寮
            ('victory', self.victory_callback),
            ('fail', self.fail_callback),
            ('award', self.award_callback),
        ]

        self.init_image_callback(prepare_callback, loop_callback)

    def person_callback(self, loc):
        self.cur_type = 'Person'
        im_yys = self.screenshot_exact()
        if self.group_done is False:
            loc_tmp = self.locate_im(self.get_image('group_transform'), im_yys)
            if loc_tmp:
                self.cur_key = 'group_transform'
                self.click_loc_one(loc_tmp)
            else:
                self.stop = True
            return

        loc_tmp = self.locate_im(self.get_image('award'), im_yys)
        if loc_tmp:
            # 挑战完 3 6 9 将之后可能会卡死在匹配上，做一层点击奖励的容错
            self.cur_key = 'award'
            self.display_msg('369次之后点击奖励')
            self.award_callback(loc_tmp)
            return

        some_box_failed = False
        if self.person_done is False:
            for box in self.person_inc_boxes:
                if self.is_inc_box_has_key('broken', box[0], box[1], box[2],
                                           box[3]):
                    continue
                elif self.is_inc_box_has_key('break_fail_person', box[0],
                                             box[1], box[2], box[3]):
                    some_box_failed = True
                    continue
                else:
                    self.cur_key = 'box_fight'
                    self._click_box_one(box)
                    time.sleep(3)  # 挑战进入比较慢，多等待3S
                    return
        if some_box_failed:
            self.display_msg('个人突破已经全部挑战完成，正在退出')
            self.stop = True

    def unselected_callback(self, loc):
        self.display_msg('寮突破还未选择突破对像，切换到个人挑战')
        self.group_done = True
        self.group_callback(loc)

    def group_callback(self, loc):
        self.cur_type = 'group'
        if self.group_done:
            im_yys = self.screenshot_exact()
            loc_tmp = self.locate_im(self.get_image('person_transform'),
                                     im_yys)
            if loc_tmp:
                self.cur_key = 'person_transform'
                self.click_loc_one(loc_tmp)
                time.sleep(1)
            else:
                self.stop = True
            return

        if self.is_inc_box_has_key('broken', self.group_inc_boxes[0][0],
                                   self.group_inc_boxes[0][1],
                                   self.group_inc_boxes[0][2],
                                   self.group_inc_boxes[0][3]):
            self.display_msg('寮突破已经全部挑战完成，正在退出')
            self.group_done = True
            return

        for box in self.group_inc_boxes:
            if self.is_inc_box_has_key('break_fail_group', box[0], box[1],
                                       box[2], box[3]):
                continue
            else:
                self._click_box_one(box)
                time.sleep(3)  # 挑战进入比较慢，多等待3S
                break

    def _check_no_ticket(self):
        im_yys = self.screenshot_exact()
        loc_tmp = self.locate_im(self.get_image('no_ticket'), im_yys)
        if loc_tmp:
            return True
        return False

    def _check_in_cd(self):
        im_yys = self.screenshot_exact()
        loc_tmp = self.locate_im(self.get_image('cd'), im_yys)
        if loc_tmp:
            return True
        return False

    def fight_callback(self, loc):
        self.cur_key = 'fight'
        self.click_loc_one(loc)
        time.sleep(0.5)
        if self._check_no_ticket():
            self.person_done = True
            self.stop = True
            self.display_msg('所有挑战券都已经用完了')

        if self._check_in_cd():
            self.group_done = True
            self.display_msg('所有寮突破已经完成，切换到其他模式')

        time.sleep(1.5)  # 界面切换比较耗时，多等待2秒

    def _click_box_one(self, box_loc):
        im_yys = self.screenshot_exact()
        loc_tmp = self.locate_im(self.get_image('fight'), im_yys)
        if loc_tmp:
            self.fight_callback(loc_tmp)
        else:
            random_x = uniform(0.4 * box_loc[2], 0.8 * box_loc[2])
            random_y = uniform(0.2 * box_loc[3], 0.8 * box_loc[3])
            self.click_loc_inc(box_loc[0] + random_x, box_loc[1] + random_y, 1)
            time.sleep(2)
            self._click_box_one(box_loc)

    def prepare_callback(self, loc):
        self.cur_key = 'prepare'
        self.click_loc_one_and_move_uncover(loc)
        time.sleep(3)
        self._mark_callback()

    def _mark_callback(self):
        im_yys = self.screenshot_exact()
        loc_tmp = self.locate_im(self.get_image('prepare'), im_yys)
        if loc_tmp:
            self.cur_key = 'prepare'
            self.click_loc_one_and_move_uncover(loc_tmp)
            time.sleep(2)
            self._mark_callback()
            return

        if self.is_inc_box_has_key('marked', self.four_role_inc_box[0],
                                   self.four_role_inc_box[1],
                                   self.four_role_inc_box[2],
                                   self.four_role_inc_box[3]):
            self.display_msg('已经标记完成')
        else:
            self.cur_key = 'marked'
            random_y = random_x = uniform(-10, 10)
            self.click_loc_inc(self.four_click_inc_pos[0] + random_x,
                               self.four_click_inc_pos[1] + random_y, 1)
            time.sleep(2)


if __name__ == '__main__':
    autogui = YysBreak()
    autogui.run('yys_break')
    logger.debug(str(autogui.prepare_image_callback))
    logger.debug(str(autogui.loop_image_callback))
