'''
Author: caiyx
Date: 2020-12-28 21:48:25
LastEditTime: 2020-12-29 11:34:59
LastEditors: Please set LastEditors
Description: 自动升级狗粮
FilePath: \new_yysscript\src\auto_yuhun.py
'''
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


class UpgradeFodder(Autogui):
    def __init__(self, win_name='阴阳师-网易游戏'):
        Autogui.__init__(self, win_name)
        # 设置当前副本的类型，设置之后优先查找御灵对应的截图
        self.screenshot.set_current_setion('upgrade')  # 设置优先的截图信息
        self.config.set_current_setion('upgrade')  # 设置当前配置信息
        self.pre_loop_times = self.config.cur_config.get('pre_loop_times', 20)
        self.loop_times = self.config.cur_config.get('loop_times', 20)
        self.stars_upgrade = self.config.cur_config.get('upgrade_stars', 2)
        self.fodder_type = self.config.cur_config.get('fodder_type', 'ncard')
        self.cur_loop_times = 0
        self.already_arrange_relax = False  # 宽松排列
        self.already_arrange_stars = False  # 按星级排列
        self.already_select_stars = False  # 选择升级的狗粮星级
        self.already_arrange_fodder = False  # 用来升级的狗粮排列类型
        self.already_change_rarity = False  # 用来设置狗粮的稀有度，即用N卡还是白蛋来喂
        self.already_in_forster = False  # 已经进入育成状态
        self.roles_boxes = [
            [49, 140, 64, 100],
            [114, 140, 64, 100],
            [178, 140, 64, 100],
            [242, 140, 64, 100],
            [49, 240, 64, 100],
            [114, 240, 64, 100],
            [178, 240, 64, 100],
            [242, 240, 64, 100],
            [49, 340, 64, 100],
            [114, 340, 64, 100],
            [178, 340, 64, 100],
            [242, 340, 64, 100],
        ]

        prepare_callback = [
            ('roles', self.click_loc_one),
        ]
        loop_callback = [
            ('task_accept', self.task_accept_callback),
            ('confirm', self.confirm_callback),
            ('yes', self.click_loc_one),
            ('foster', self.foster_callback),
        ]

        self.init_image_callback(prepare_callback, loop_callback)

    def _arrage_relax(self):
        '''选择宽松排列'''
        loc_tmp = self.locate_im(self.get_image('order_type'))
        if loc_tmp:
            self.click_loc_one(loc_tmp)
            time.sleep(1)
            self.cur_key = 'order_relax'
            loc_relax = self.locate_im(self.get_image('order_relax'))
            if loc_relax:
                self.display_msg('标记宽松排列')
                self.already_arrange_relax = True
                self.click_loc_one(loc_relax)
            time.sleep(1)

    def _arrage_stars(self):
        '''选择按星级排列'''
        if self.locate_im(self.get_image('star2')):
            self.already_arrange_stars = True
            return

        loc_stars = self.locate_im(self.get_image('order_by_star'))
        if loc_stars:
            self.cur_key = 'order_by_star'
            self.display_msg('标记按星级排列')
            self.already_arrange_stars = True
            self.click_loc_one(loc_stars)
            time.sleep(0.5)
            return

        loc_type = self.locate_im(self.get_image('order_type'))
        if loc_type:
            self.cur_key = 'order_type'
            self.click_loc_one(loc_type)
            time.sleep(1)
            self._arrage_stars()
            time.sleep(1)

    def _select_stars(self):
        '''选择要升级的狗粮星级'''
        self.display_msg('选择星级：{0}'.format(self.stars_upgrade))
        if self.stars_upgrade == 3:
            loc_star = self.locate_im(self.get_image('star3'), confidence=0.9)
        else:
            loc_star = self.locate_im(self.get_image('star2'))
        self.already_select_stars = True
        self.display_msg('选择要升级的狗粮星级,{0}->{1}'.format(self.stars_upgrade,
                                                      self.stars_upgrade + 1))
        self.cur_key = 'select_stars'
        self.click_loc_one(loc_star)
        time.sleep(0.5)

    def foster_callback(self, loc):
        roles_boxes = self.roles_boxes
        if self.already_arrange_relax is False:
            self._arrage_relax()
            return

        if self.already_arrange_stars is False:
            self._arrage_stars()
            return

        if self.already_select_stars is False:
            self._select_stars()
            return

        if self.already_in_forster is False:
            for i in range(len(roles_boxes)):
                loc_tmp = self.locate_im_inc(self.get_image('man'),
                                             roles_boxes[i][0],
                                             roles_boxes[i][1],
                                             roles_boxes[i][2],
                                             roles_boxes[i][3])
                if loc_tmp:
                    random_x = uniform(roles_boxes[i][2] * 0.4,
                                       roles_boxes[i][2] * 0.7)
                    random_y = uniform(roles_boxes[i][3] * 0.4,
                                       roles_boxes[i][3] * 0.7)
                    self.display_msg('选择狗粮{0}, ({1}，{2})'.format(
                        i, roles_boxes[i][0] + random_x,
                        roles_boxes[i][1] + random_y))
                    self.cur_key = 'select_fodder'
                    self.click_loc_inc(roles_boxes[i][0] + random_x,
                                       roles_boxes[i][1] + random_y, 1)
                    time.sleep(0.5)
                    break
            if i == len(roles_boxes):
                self.display_msg('已经没有满级狗粮可以拿来升级，退出')
                self.stop = True

            loc_tmp = self.locate_im(self.get_image('foster'))
            if loc_tmp:
                self.cur_key = 'foster'
                self.display_msg('已经选中要升级的狗粮，点击育成')
                self.click_loc_one(loc_tmp)

    def confirm_callback(self, loc):
        '''选择要作为狗粮的N卡或者白蛋'''
        roles_boxes = self.roles_boxes
        if self.already_change_rarity is False:
            self.already_change_rarity = True
            '''如果已经是按稀有度排序，就不再重新选择了'''
            if self.locate_im(self.get_image('ncard')) is None:
                loc_tmp = self.locate_im(self.get_image('fodder_select'))
                if loc_tmp:
                    self.cur_key = 'fodder_select'
                    self.click_loc_inc(loc_tmp.left + 10, loc_tmp.top + 10, 1)
                    time.sleep(0.5)
                loc_tmp = self.locate_im(self.get_image('rarity'))
                if loc_tmp:
                    self.display_msg('按稀有度排序作为狗粮的式神')
                    self.cur_key = 'order_by_rarity'
                    self.click_loc_one(loc_tmp)
                    time.sleep(0.5)

        loc_tmp = self.locate_im(self.get_image(self.fodder_type))
        if loc_tmp:
            self.display_msg('选择{0}作为狗粮'.format(self.fodder_type))
            self.cur_key = 'select ' + self.fodder_type
            self.click_loc_one(loc_tmp)
            time.sleep(0.5)

        if self.already_arrange_fodder is False:
            self.already_arrange_fodder = True
            loc_tmp = self.locate_im(self.get_image('fodder_relax'))
            if loc_tmp:
                self.display_msg('宽松排列作为狗粮的式神')
                self.cur_key = 'fodder_relax'
                self.click_loc_one(loc_tmp)
                time.sleep(0.5)

        for i in range(self.stars_upgrade):
            random_x = uniform(roles_boxes[i][2] * 0.4,
                               roles_boxes[i][2] * 0.7)
            random_y = uniform(roles_boxes[i][3] * 0.4,
                               roles_boxes[i][3] * 0.7)
            self.display_msg('选择狗粮{0}, ({1}，{2})'.format(
                i, roles_boxes[i][0] + random_x, roles_boxes[i][1] + random_y))
            self.cur_key = 'select_fodder'
            self.click_loc_inc(roles_boxes[i][0] + random_x,
                               roles_boxes[i][1] + random_y, 1)
            time.sleep(0.5)
        '''点击确认升级狗粮'''
        self.cur_key = 'upgrade'
        self.display_msg('升级第{0}只狗粮'.format(self.cur_loop_times))
        self.click_loc_one(loc)
        self.cur_loop_times += 1
        self.already_in_forster = False  # 将正在升级的标记清空掉
        time.sleep(0.5)
        '''狗粮不足时，自动退出升级'''
        loc_tmp = self.locate_im(self.get_image('not_enough'))
        if loc_tmp:
            self.display_msg('狗粮不足，正在退出')
            self.stop = True
        time.sleep(2)  # 升级一只后动画比较长，等待2秒


if __name__ == '__main__':
    autogui = UpgradeFodder()
    autogui.run('upgrade')
    logger.debug(str(autogui.prepare_image_callback))
    logger.debug(str(autogui.loop_image_callback))
