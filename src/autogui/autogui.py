#!/usr/bin/python
# -*- coding: utf-8 -*

# %% 先加载对应的库
import os
import sys
import time
import pyautogui
from win_gui import Yys_windows_GUI
from PyQt5.QtCore import pyqtSignal, QThread
from random import randint, uniform

# 将上一层目录添加到系统目录
cur_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]
par_dir = os.path.split(os.path.abspath(cur_dir))[0]
sys.path.append(par_dir)

# 使用opencv的图片匹配函数，如果不想用opencv可以使用 screenshot_pil.py 脚本
from config import YysConfig
import screenshot

locate = screenshot.locate_image_cv2pil
YysScreenshot = screenshot.YysScreenshot


class ImageCallback():
    def __init__(self, key, image, callback):
        self.key = key
        self.image = image
        self.callback = callback


class Autogui(QThread):
    # 定义类属性为信号函数
    sendmsg = pyqtSignal(str, str)  # type, msg

    def __init__(self, win_name='阴阳师-网易游戏'):
        super(Autogui, self).__init__(None)  # 初始化信号和槽的初始化
        self.win_name = win_name
        self.window = Yys_windows_GUI(self.win_name)
        self.auto_type = ''  # 当前执行的脚本类型
        self.init_config()  # 获取配置
        self.init_screenshot()  # 获取截图信息
        self.prepare_image_callback = []  # ImageCallback
        self.loop_image_callback = []  # ImageCallback
        self.stop = False  # 是否停止脚本
        self.cur_key = ''  # 当前匹配的key，用来输出日志
        self.cur_loop_times = 0  # 当前循环数
        self.last_key = ''  # 上一次循环的key，用来检测死循环

    def init_config(self):
        yys_config = YysConfig(name='yys_config')
        self.config = yys_config
        general_keys = [
            ('title', 'str', 'x笑cry-辅助工具'),
            ('version', 'str', 'v1.0.0'),
            ('gitpath', 'str', '无'),
            ('attention', 'str', '无'),
            ('drag_dis', 'int', 8),  # 狗粮拖动距离
            ('width', 'int', 8),
            ('height', 'int', 8),
        ]
        yuling_keys = [
            ('loop_times', 'int', 200),
            ('type', 'str', 'dragon'),
            ('layer', 'int', 3),
            ('attention', 'str', ''),
        ]
        break_keys = [
            ('loop_times', 'int', 200),
            ('attention', 'str', ''),
        ]
        chapter_keys = [
            ('loop_times', 'int', 200),
            ('players', 'int', 2),
            ('captain', 'bool', True),
            ('attention', 'str', ''),
        ]

        yuhun_keys = [
            ('loop_times', 'int', 200),
            ('players', 'int', 2),
            ('captain', 'bool', True),
            ('attention', 'str', ''),
        ]

        wangzhe_keys = [
            ('loop_times', 'int', 50),
            ('attention', 'str', ''),
        ]

        yys_config.read_one_type_config('general', general_keys)
        # print(getattr(yys_config, 'general'))
        yys_config.read_one_type_config('yuling', yuling_keys)
        # print(getattr(yys_config, 'yuling'))
        yys_config.read_one_type_config('yys_break', break_keys)
        # print(getattr(yys_config, 'break'))
        yys_config.read_one_type_config('chapter', yuhun_keys)
        # print(getattr(yys_config, 'chapter'))
        yys_config.read_one_type_config('yuhun', chapter_keys)
        # print(getattr(yys_config, 'chapter'))
        yys_config.read_one_type_config('wangzhe', wangzhe_keys)
        # print(getattr(yys_config, 'wangzhe'))

    def init_screenshot(self):
        self.screenshot = YysScreenshot('')

    def already_in_loop(self, im_yys):
        if len(self.prepare_image_callback) == 0:
            self.display_msg('默认已经是可循环状态')
            return True

        if im_yys is None:
            im_yys = self.screenshot_exact()
        for callback in self.loop_image_callback:
            if self.locate_im(callback.image, im_yys):
                self.display_msg('匹配{0}，可以进入循环'.format(callback.key))
                return True
        self.display_msg(self.cur_key + ': 当前状态还不能进入到可循环状态')
        return False

    def run(self, auto_type: str):
        self.auto_type = auto_type
        if self.resize_window_size(self.config.general['width'],
                                   self.config.general['height']) is False:
            self.display_msg('调整窗体大小失败')
            return
        self.display_msg('正在尝试进入循环')
        if self.goto_loop() is False:
            self.display_msg('无法进入循环')
            return
        self.display_msg('成功进入循环脚本')
        self.display_msg(str(self.config.cur_config))  # 打印配置信息
        self.loop()

    def goto_loop(self):
        self.cur_loop_times = 0
        while self.stop is False and self.cur_loop_times < self.pre_loop_times:
            im_yys = self.screenshot_exact()
            found = False
            if self.already_in_loop(im_yys):
                return True

            im_yys = self.screenshot_exact()  # 执行操作之后需要重新获取截图
            for callback in self.prepare_image_callback:
                self.cur_loop_times += 1
                loc = self.locate_im(callback.image, im_yys)
                if loc is None:
                    print(callback.key, ' not match')
                    continue
                self.cur_key = callback.key
                callback.callback(loc)  # 执行对应的回调
                time.sleep(1)
                found = True
                break

            if found is False:
                time.sleep(1)
        return False

    def loop(self):
        self.cur_loop_times = 0
        while self.stop is False and self.cur_loop_times < self.loop_times:
            im_yys = self.screenshot_exact()
            found = False

            im_yys = self.screenshot_exact()  # 执行操作之后需要重新获取截图
            for callback in self.loop_image_callback:
                loc = self.locate_im(callback.image, im_yys)
                if loc is None:
                    continue
                self.cur_key = callback.key
                callback.callback(loc)  # 执行对应的回调
                time.sleep(0.5)
                found = True
                break

            if found is False:
                time.sleep(1)

    def raise_msg(self, msg):
        '''输出日志到框内，且弹窗提醒错误'''
        print(msg)
        self.sendmsg.emit(msg, 'Error')

    def display_msg(self, msg):
        '''输出日志到框内'''
        print(msg)
        self.sendmsg.emit(msg, 'Info')

    def get_window_handler(self):
        return self.window.get_window_handler()

    def resize_window_size(self, width, height):
        return self.window.resize_window_size(width, height)

    def get_image(self, key):
        return self.screenshot.get_jpg(key)

    def init_image_callback(self, prepare_callback, loop_callback):
        '''格式化图片文件及对应的callback'''
        for each_callback in prepare_callback:
            callback = ImageCallback(each_callback[0],
                                     self.get_image(each_callback[0]),
                                     each_callback[1])
            self.prepare_image_callback.append(callback)
        for each_callback in loop_callback:
            callback = ImageCallback(each_callback[0],
                                     self.get_image(each_callback[0]),
                                     each_callback[1])
            self.loop_image_callback.append(callback)

    def screenshot_exact(self, x=0, y=0, w=0, h=0):
        '''默认截取yys整个页面，成功返回截图，失败返回None'''
        try:
            if x == 0 and y == 0 and w == 0 and h == 0:
                im = pyautogui.screenshot(region=(self.window.x_top,
                                                  self.window.y_top,
                                                  self.window.win_width,
                                                  self.window.win_height))
            else:
                im = pyautogui.screenshot(region=(x, y, w, h))
            return im
        except Exception:
            # self.display_msg('截图失败：' + str(error))
            return None

    def screenshot_inc(self, x=0, y=0, w=0, h=0):
        '''默认截取yys相对位置，成功返回截图，失败返回None'''
        w = w if w != 0 else self.window.win_width
        h = h if h != 0 else self.window.win_height
        return self.screenshot_exact(self.window.x_top + x,
                                     self.window.y_top + y, w, h)

    def locate_im(self, check_im, basic_im=None, confidence=0.8):
        '''检查图片是否存在, (Image, Image) -> loc or None'''
        try:
            if basic_im is None:
                im_yys = self.screenshot_exact()
            else:
                im_yys = basic_im
            loc = locate(check_im, im_yys, confidence=confidence)
            return loc
        except Exception as error:
            self.display_msg('截图比对失败：' + str(error))
            return None

    def locate_im_exact(self, check_im, x, y, w, h, confidence=0.8):
        '''通过坐标来获取截图并查看图片是否存在'''
        try:
            im_yys = self.screenshot_exact(x, y, w, h)
            loc = locate(check_im, im_yys, confidence=confidence)
            # im_yys.show()
            return loc
        except Exception as error:
            self.display_msg('截图比对失败：' + str(error))
            return None

    def locate_im_inc(self, check_im, x, y, w, h):
        '''通过坐标来获取截图并查看图片是否存在'''
        return self.locate_im_exact(check_im, self.window.x_top + x,
                                    self.window.y_top + y, w, h)

    def locate_ims(self, check_ims):
        '''检验一组图片截图是否在界面当中，存在时返回对应的 loc'''
        im_yys = self.screenshot_exact()
        for im in check_ims:
            loc = self.locate_im(im, im_yys)
            if loc:
                return loc
        return None

    # %% 移动鼠标(0.5S)，取截图位置的偏中间位置，并触发鼠标点击，点击2次，间隔随机0-1S
    def click_loc(self, loc, times=-1):
        random_x = uniform(loc.width * 0.3, loc.width * 0.6)
        random_y = uniform(loc.height * 0.3, loc.height * 0.6)
        interval = uniform(0.2, 0.5)
        click_x = self.window.x_top + loc.left + random_x
        click_y = self.window.y_top + loc.top + random_y
        self.click_loc_exact(click_x, click_y, times, interval)

    def check_bad_loop(self, key):
        if key != self.last_key:
            self.last_key = key
            self.last_key_loop_times = 1
        else:
            self.last_key_loop_times += 1
            if self.last_key_loop_times > 50:
                self.display_msg('可能触发了死循环：{0}'.format(self.last_key))
            elif self.last_key_loop_times % 10 == 0:
                self.display_msg('{0}循环了{1}次'.format(self.last_key,
                                                     self.last_key_loop_times))

    def click_loc_exact(self, click_x, click_y, times=-1, interval=0.5):
        if times == -1:
            times = randint(2, 3)
        random_dis = uniform(-0.5, 0.5)
        click_x += random_dis
        click_y += random_dis
        self.display_msg('点击位置：({0},{1},{2},{3})'.format(
            click_x, click_y, interval, times))
        pyautogui.click(click_x, click_y, times, interval, button='left')
        self.display_msg('点击：{0}进入下一步'.format(self.cur_key))
        self.check_bad_loop(self.cur_key)

    def click_loc_inc(self, inc_x, inc_y, times=-1, interval=0.5):
        return self.click_loc_exact(self.window.x_top + inc_x,
                                    self.window.y_top + inc_y, times, interval)

    def click_loc_one(self, loc):
        self.click_loc(loc, 1)

    def click_loc_twice(self, loc):
        self.click_loc(loc, 2)

    def move_uncover(self, loc):
        random_x = uniform(-2.0 * loc.width, -1.0 * loc.width)
        random_y = uniform(-2.0 * loc.height, -1.0 * loc.height)
        interval = uniform(0.1, 0.5)
        move_x = self.window.x_top + loc.left + random_x
        move_y = self.window.y_top + loc.top + random_y
        self.display_msg('偏移位置以防遮挡：({0},{1})'.format(move_x, move_y))
        pyautogui.moveTo(move_x, move_y, duration=interval)

    def move_uncover_to_right(self, loc):
        random_x = uniform(1.0 * loc.width, 2.0 * loc.width)
        random_y = uniform(1.0 * loc.height, 2.0 * loc.height)
        interval = uniform(0.1, 0.5)
        move_x = self.window.x_top + loc.left + random_x
        move_y = self.window.y_top + loc.top + random_y
        self.display_msg('偏移位置以防遮挡：({0},{1})'.format(move_x, move_y))
        pyautogui.moveTo(move_x, move_y, duration=interval)

    def click_loc_one_and_move_uncover(self, loc):
        self.click_loc_one(loc)
        self.move_uncover(loc)

    def move_loc_exact(self, move_x, move_y, interval=0):
        interval = interval if interval != 0 else uniform(0.1, 0.5)
        self.display_msg('移动位置到：({0},{1})'.format(move_x, move_y))
        pyautogui.moveTo(move_x, move_y, duration=interval)

    def move_loc_inc(self, move_x, move_y, interval=0):
        '''移动相对于主界面的相对位置'''
        interval = interval if interval != 0 else uniform(0.1, 0.5)
        self.display_msg('移动位置到：({0},{1})'.format(move_x, move_y))
        pyautogui.moveTo(self.window.x_top + move_x,
                         self.window.y_top + move_y,
                         duration=interval)

    def scroll_loc_exact(self, clicks, move_x=0, move_y=0):
        '''滚动接口调用之后点击位置会不准
            clicks 参数表示滚动的格数。
            正数则页面向上滚动
            负数则向下滚动
        '''
        self.display_msg('滚动鼠标幅度：{0}'.format(clicks))
        pyautogui.scroll(clicks=clicks, x=move_x, y=move_y)

    def dragRel_loc_exact(self, x_offset, y_offset, du=0.5):
        '''
            @x_offset： 正数为按住一个点向右拖动，负数按住一个点向左拖动
            @y_offset： 正数为按住一个点向下拖动，负数按住一个点向上拖动，大小表示拖动幅度
            @du, 表示拖动使用的时间间隔滚动
        '''
        self.display_msg('拖动鼠标幅度：{0}, {1}'.format(x_offset, y_offset))
        pyautogui.dragRel(x_offset, y_offset, duration=du)

    def click_success_check(self, key, callback, *args):
        im_yys = self.screenshot_exact()
        loc = self.locate_im(self.get_image(key), im_yys)
        if loc:
            if len(args) == 0:
                callback(loc)
            else:
                callback(loc, args)

    def void_callback(self, loc):
        self.display_msg('空操作：{0}，等待1S'.format(self.cur_key))
        time.sleep(1)

    def task_accept_callback(self, loc):
        im_yys = self.screenshot_exact()
        loc_tmp = self.locate_im(self.get_image('accept'), im_yys)
        if loc_tmp:
            self.click_loc_one(loc_tmp)
            return

    def prepare_callback(self, loc):
        self.click_loc_one_and_move_uncover(loc)
        time.sleep(1)
        self.click_success_check('prepare', self.prepare_callback)

    def click_loc_one_when_award(self):
        im_yys = self.screenshot_exact()
        loc_tmp = self.locate_im(self.get_image('victory'), im_yys)
        if loc_tmp:
            self.click_loc_twice(loc_tmp)
            return
        loc_tmp = self.locate_im(self.get_image('award'), im_yys)
        if loc_tmp:
            self.click_loc_twice(loc_tmp)
            return
        loc_tmp = self.locate_im(self.get_image('fail'), im_yys)
        if loc_tmp:
            self.click_loc_twice(loc_tmp)
            return
        loc_tmp = self.locate_im(self.get_image('continue'), im_yys)
        if loc_tmp:
            self.click_loc_twice(loc_tmp)
            return

    def victory_callback(self, loc):
        self.display_msg('当前进度：{0}/{1}'.format(self.cur_loop_times + 1,
                                               self.loop_times))
        self.click_loc_one_when_award()
        time.sleep(1)
        self.cur_loop_times += 1
        self.click_success_check('victory', self.victory_callback)

    def fail_callback(self, loc):
        self.click_loc_one_when_award()
        time.sleep(1)
        self.click_success_check('fail', self.fail_callback)

    def award_callback(self, loc):
        self.click_loc_one_when_award()
        time.sleep(2)
        self.click_success_check('award', self.award_callback)

    def fight_callback(self, loc):
        pass

    def is_inc_box_has_key(self, key, x, y, w, h):
        return self.locate_im_inc(self.get_image(key), x, y, w, h) is not None

    def get_all_images(self, key, im_yys=None, confidence=0.8):
        if im_yys is None:
            im_yys = self.screenshot_exact()
        locs = screenshot.locate_im_cv2pil(self.get_image(key),
                                           im_yys,
                                           confidence,
                                           multi_loc=True)
        if locs is None:
            return 0
        else:
            return locs
