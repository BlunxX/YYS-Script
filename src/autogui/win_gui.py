#!/usr/bin/python
# -*- coding: utf-8 -*

import win32gui
import win32con
import logging
from PyQt5.QtCore import QObject, pyqtSignal, QThread


class Yys_GUI(QThread):
    # 定义类属性为信号函数
    sendmsg = pyqtSignal(str, str)  # type, msg

    def __init__(self, win_name='阴阳师-网易游戏'):
        self.win_name = win_name
        super(Yys_GUI, self).__init__(None)     # 需要初始化，否则会报异常

    def get_window_handle(self):
        pass

    def resize_window_size(self, width, height):
        pass

    def raise_msg(self, msg):
        '''输出日志到框内，且弹窗提醒错误'''
        print(msg)
        self.sendmsg.emit(msg, 'Error')

    def display_msg(self, msg):
        '''输出日志到框内'''
        print(msg)
        self.sendmsg.emit(msg, 'Info')


class Yys_windows_GUI(Yys_GUI):

    sendmsg = pyqtSignal(str, str)  # type, msg

    def __init__(self, win_name='阴阳师-网易游戏'):
        # 获取窗体的特性
        Yys_GUI.__init__(self, win_name)
        self.handler = None
        self.x_top = self.y_top = self.x_bottom = self.y_bottom = 0
        self.win_width = self.win_height = 0

    def get_window_handler(self):
        '''获取到阴阳师窗体信息'''
        handler = win32gui.FindWindow(0, self.win_name)  # 获取窗口句柄
        if handler == 0:
            self.raise_msg('捕获不到程序：' + self.win_name)
            return False
        self.handler = handler
        self.x_top, self.y_top, self.x_bottom, self.y_bottom = \
            win32gui.GetWindowRect(handler)
        self.win_width = self.x_bottom - self.x_top
        self.win_height = self.y_bottom - self.y_top
        self.display_msg('捕获到程序：{0},({1},{2}),{3},{4}'.format(
            self.win_name, self.x_top, self.y_top, self.win_width,
            self.win_height))

        logging.info(
            '位置信息：top({0},{1}), bottom({2},{3}), width:{4}, height:{5} '.
            format(self.x_top, self.y_top, self.x_bottom, self.y_bottom,
                   self.win_width, self.win_height))
        return True

    def resize_window_size(self, width=800, height=480):
        '''设置固定大小，方便后续截图和比对，这里比较有限制'''
        if self.get_window_handler() is False:
            self.raise_msg('请确认程序有开启' + self.win_name)
            return False

        # reset win and update win info
        try:
            win32gui.SetWindowPos(self.handler, win32con.HWND_NOTOPMOST,
                                  self.x_top, self.y_top, width, height,
                                  win32con.SWP_SHOWWINDOW)
            self.get_window_handler()
        except Exception as error:
            self.raise_msg('请确认你拥有管理员权限，否则无法重新设置大小，msg:{0}'.format(error))
            return False
        return True
