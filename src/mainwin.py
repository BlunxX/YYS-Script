# -*- coding: utf-8 -*-

import os
import sys

cur_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]
# ui_path = os.path.abspath(cur_dir + os.path.sep + "..") + os.path.sep + 'ui'
ui_path = cur_dir + os.path.sep + 'ui'
images_path = cur_dir + os.path.sep + 'screenshot'
tools_path = cur_dir + os.path.sep + 'tools'
sys.path.append(tools_path)
sys.path.append(ui_path)
sys.path.append(images_path)

import images
import time
import datetime
import licence
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
from auto_chapter28 import Chapter
from auto_wangzhe import Wangzhe
from auto_break import YysBreak
from auto_yuling import Yuling
from auto_yuhun import Yuhun
from auto_upgrade import UpgradeFodder
from auto_yeyuanhuo import Yeyuanhuo
from auto_pattern import Pattern
from config import YysConfig
from main_widget import Ui_yys_win


class YysWin(QMainWindow):
    stop_run = pyqtSignal()

    def __init__(self, parent=None, win_name='阴阳师-网易游戏'):
        # Ui_yys_win.__init__(self)
        super(YysWin, self).__init__(parent)
        self.ui = Ui_yys_win()
        self.ui.setupUi(self)

        self.ui.pte_msg.clear()  # 清理界面
        self.init_config()  # 获取到配置
        self.show_attention(self.config.general['attention'])
        self.setWindowTitle(self.config.general['title'])
        self.setWindowIcon(QIcon(":/icon/images/zhangliang.ico"))
        # '王者荣耀',
        funcs = ["御魂", "困28", "御灵", "业原火", "结界突破", '升级狗粮', '点击模式']
        self.set_ui_cmbox(self.ui.cb_fuctions, funcs)
        self.init_cb_fuctions(self.ui.cb_fuctions.currentText())

        # 不设置群号信息了
        # self.ui.lb_qrcode.setPixmap(QPixmap(":/images/images/qun.jpg"))

        # 绑定信号和槽
        self.ui.pbt_autocheck.clicked.connect(self.btn_autocheck_clicked)

        # 功能选项
        self.has_start = False
        self.select_fun = self.ui.cb_fuctions.currentText()

        # 时间认证
        self.check_licence()

    def init_cb_fuctions(self, func_name):
        self.select_fun = self.ui.cb_fuctions.currentText()
        titles = []
        attentions = self.config.general['attention']
        times = ['挂机次数']
        times.extend([str(x * 10) for x in range(1, 11)])
        times.extend(['200', '400', '9999'])
        if self.select_fun == '御魂':
            attentions = self.config.yuhun['attention']
            titles = [['单人', '双人', '三人'], ['队长', '队员'], times]
        elif self.select_fun == '困28':
            attentions = self.config.chapter['attention']
            titles = [['单人', '双人'], ['队长', '队员'], times, ['狗粮类型', 'N卡', '白蛋']]
        elif self.select_fun == '御灵':
            attentions = self.config.yuling['attention']
            titles = [['挑战类型', 'dragon', 'fox', 'leopard', 'phenix'], times]
        elif self.select_fun == '结界突破':
            attentions = self.config.yys_break['attention']
            titles = []
        elif self.select_fun == '升级狗粮':
            attentions = self.config.upgrade['attention']
            titles = [['升星等级', '2->3', '3->4'], times]
        elif self.select_fun == '业原火':
            attentions = self.config.yeyuanhuo['attention']
            titles = [['更换狗粮', '不更换'], times, ['狗粮类型', 'N卡', '白蛋']]
        elif self.select_fun == '点击模式':
            attentions = self.config.yeyuanhuo['attention']
            titles = [ times]
        self.show_attention(attentions)
        self.set_comboxes(titles)

    def init_config(self):
        if hasattr(self, 'config') and self.config is not None:
            self.display_msg('参数已经初始化完成')
            self.display_msg(str(self.config))
            return

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
            ('licence', 'str', 'ABC'),
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
            ('players', 'int', 1),
            ('captain', 'bool', True),
            ('fodder_type', 'str', 'fodder'),
            ('drag', 'int', 5),
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

        upgrade_keys = [
            ('loop_times', 'int', 50),
            ('upgrade_stars', 'int', 2),
            ('attention', 'str', ''),
        ]

        yeyuanhuo_keys = [
            ('loop_times', 'int', 100),
            ('fodder_type', 'str', 'fodder'),
            ('drag', 'int', 5),
            ('attention', 'str', ''),
            ('change_fodder', 'bool', True),
        ]

        pattern_keys = [
            ('loop_times', 'int', 100),
            ('attention', 'str', ''),
            ('winname', 'str', 'None'),
            ('prepare_keys', 'str', ''),
            ('loop_keys', 'str', ''),
        ]

        yys_config.read_one_type_config('general', general_keys)
        # print(getattr(yys_config, 'general'))
        yys_config.read_one_type_config('yuling', yuling_keys)
        # print(getattr(yys_config, 'yuling'))
        yys_config.read_one_type_config('yys_break', break_keys)
        # print(getattr(yys_config, 'yys_break'))
        yys_config.read_one_type_config('chapter', chapter_keys)
        # print(getattr(yys_config, 'chapter'))
        yys_config.read_one_type_config('yuhun', yuhun_keys)
        # print(getattr(yys_config, 'yuhun'))
        yys_config.read_one_type_config('upgrade', upgrade_keys)
        # print(getattr(yys_config, 'upgrade'))
        yys_config.read_one_type_config('yeyuanhuo', yeyuanhuo_keys)
        # print(getattr(yys_config, 'yeyuanhuo'))
        yys_config.read_one_type_config('wangzhe', wangzhe_keys)
        # print(getattr(yys_config, 'wangzhe'))
        yys_config.read_one_type_config('pattern', pattern_keys)
        # print(getattr(yys_config, 'pattern'))

    def display_msg(self, msg, type='Info'):
        if (type == 'Info'):
            '''输出日志到框内'''
            self.ui.pte_msg.moveCursor(QtGui.QTextCursor.End)
            self.ui.pte_msg.insertPlainText(msg + '\n')
        else:
            self.raise_msg(msg)

    def raise_msg(self, msg):
        '''输出日志到框内，且弹窗提醒错误'''
        self.display_msg(msg + '\n')

    def clean_msg(self):
        '''清理日志输出框'''
        self.ui.pte_msg.clear()

    def set_ui_cmbox(self, cb, lines):
        '''给一个具体的combox控件添加显示项目'''
        cb.clear()
        cb.addItems(lines)

    def set_comboxes(self, titles: list):
        '''通过列表来设置参数'''
        comboxes = [
            self.ui.cb_p1, self.ui.cb_p2, self.ui.cb_p3, self.ui.cb_p4,
            self.ui.cb_p5, self.ui.cb_p6
        ]
        titles_len = len(titles)
        for i in range(6):
            if i < titles_len:
                self.set_ui_cmbox(comboxes[i], titles[i])
            else:
                self.set_ui_cmbox(comboxes[i], ['参数{}'.format(i + 1)])

    def cb_functions_index_changed(self):
        self.init_cb_fuctions(self.ui.cb_fuctions.currentText())

    def cb_p1_index_changed(self):
        pass

    def cb_p2_index_changed(self):
        pass

    def cb_p3_index_changed(self):
        pass

    def cb_p4_index_changed(self):
        pass

    def cb_p5_index_changed(self):
        pass

    def cb_p6_index_changed(self):
        pass

    def _set_loop_times(self, configs, times_str):
        configs['loop_times'] = 9999
        try:
            configs['loop_times'] = int(times_str)
        except Exception as error:
            configs['loop_times'] = 9999
            self.display_msg('设置默认值为：9999， error={0}'.format(error))

    def set_yuhun_config(self, cb_texts):
        # titles = [['单人', '双人', '三人'], ['队长', '队员'], times]
        configs = self.config.yuhun

        if cb_texts[0] == '双人':
            configs['players'] = 2
        elif cb_texts[0] == '单人':
            configs['players'] = 1
        else:
            configs['players'] = 3

        configs['captain'] = True if cb_texts[1] == '队长' else False
        self._set_loop_times(configs, cb_texts[2])

    def set_chapter_config(self, cb_texts):
        # titles = [['单人', '双人'], ['队长', '队员'], times, ['狗粮类型', 'N卡', '白蛋']]
        configs = self.config.chapter

        configs['players'] = 2 if cb_texts[0] == '双人' else 1
        configs['captain'] = True if cb_texts[1] == '队长' else False
        self._set_loop_times(configs, cb_texts[2])
        configs['fodder_type'] = 'ncard' if cb_texts[3] == 'N卡' else 'fodder'

    def set_yuling_config(self, cb_texts):
        # titles = [['挑战类型', 'dragon', 'fox', 'leopard', 'phenix'], times]
        configs = self.config.yuling
        configs['type'] = cb_texts[0] if cb_texts[0] != '挑战类型' else 'phenix'
        self._set_loop_times(configs, cb_texts[2])

    def set_break_config(self, cb_texts):
        pass

    def set_wangzhe_config(self, cb_texts):
        # titles = [times]
        configs = self.config.wangzhe
        self._set_loop_times(configs, cb_texts[0])

    def set_upgrade_config(self, cb_texts):
        # titles = [['升星等级', '2->3', '3->4'], times]
        configs = self.config.upgrade
        configs['upgrade_stars'] = 3 if cb_texts[0] == '3->4' else 2
        self._set_loop_times(configs, cb_texts[1])

    def set_yeyuanhuo_config(self, cb_texts):
        # titles = [['更换狗粮', '不更换'], times, ['狗粮类型', 'N卡', '白蛋']]
        configs = self.config.yeyuanhuo
        configs['change_fodder'] = True if cb_texts[0] == '更换狗粮' else False
        self._set_loop_times(configs, cb_texts[1])
        configs['fodder_type'] = 'ncard' if cb_texts[3] == 'N卡' else 'fodder'

    def set_pattern_config(self, cb_texts):
        # titles = [times]
        configs = self.config.pattern
        self._set_loop_times(configs, cb_texts[0])

    def get_config_from_param_cb(self):
        cb_texts = []
        cb_texts.append(self.ui.cb_p1.currentText())
        cb_texts.append(self.ui.cb_p2.currentText())
        cb_texts.append(self.ui.cb_p3.currentText())
        cb_texts.append(self.ui.cb_p4.currentText())
        cb_texts.append(self.ui.cb_p5.currentText())
        cb_texts.append(self.ui.cb_p6.currentText())

        if self.select_fun == '御魂':
            self.set_yuhun_config(cb_texts)
        elif self.select_fun == '困28':
            self.set_chapter_config(cb_texts)
        elif self.select_fun == '御灵':
            self.set_yuling_config(cb_texts)
        elif self.select_fun == '结界突破':
            self.set_break_config(cb_texts)
        elif self.select_fun == '王者荣耀':
            self.set_wangzhe_config(cb_texts)
        elif self.select_fun == '升级狗粮':
            self.set_upgrade_config(cb_texts)
        elif self.select_fun == '业原火':
            self.set_yeyuanhuo_config(cb_texts)
        elif self.select_fun == '点击模式':
            self.set_pattern_config(cb_texts)

    def check_licence(self):
        '''设置过期时间'''
        self.licence_unexpired = licence.check_license(
            self.config.general['licence'])
        if self.licence_unexpired is False:
            self.display_msg('认证失败或认证已过期')
        else:
            self.display_msg(
                licence.get_remain_time(self.config.general['licence']))

    def btn_autocheck_clicked(self):
        self.display_msg('自动挂机检测：{0}'.format(
            self.ui.cb_fuctions.currentText()))
        self.stop_run.emit()

    def btn_restart_clicked(self):
        self.btn_stop_clicked()
        self.btn_start_clicked()

    def btn_stop_clicked(self):
        self.display_msg('停止挂机：{0}'.format(self.select_fun))
        self.has_start = False
        self.stop_run.emit()
        self.show_attention(self.config.general['attention'] + '\n' +
                            self.config.general['version'])

    def btn_start_clicked(self):
        if self.licence_unexpired is False:
            self.display_msg('认证已经过期，即将退出...')
            return

        if self.has_start is True:
            self.display_msg('挂机已启动，请务重新启动，{0}' + self.select_fun)
            return

        # 从参数列表中选择参数
        self.get_config_from_param_cb()
        self.display_msg('启动挂机：{0}'.format(self.select_fun))
        self.autogui = None
        if self.select_fun == '御魂':
            self.autogui = Yuhun()
            self.auto_type = 'yuhun'
        elif self.select_fun == '御灵':
            self.autogui = Yuling()
            self.auto_type = 'yuling'
        elif self.select_fun == '困28':
            self.autogui = Chapter()
            self.auto_type = 'chapter'
        elif self.select_fun == '结界突破':
            self.autogui = YysBreak()
            self.auto_type = 'break'
        elif self.select_fun == '王者荣耀':
            self.autogui = Wangzhe()
            self.auto_type = 'wangzhe'
        elif self.select_fun == '升级狗粮':
            self.autogui = UpgradeFodder()
            self.auto_type = 'upgrade'
        elif self.select_fun == '业原火':
            self.autogui = Yeyuanhuo()
            self.auto_type = 'yeyuanhuo'
        elif self.select_fun == '点击模式':
            self.autogui = Pattern()
            self.auto_type = 'pattern'
            self.autogui.window.set_only_getwin(True)
        self.has_start = True
        self.autogui.sendmsg.connect(self.display_msg)
        self.stop_run.connect(self.autogui.stop_run)
        self.autogui.start()

    def show_attention(self, contenet):
        contenet = contenet.replace(r'\n', '\n')
        self.ui.te_attention.setText(contenet + '\n开源地址：' +
                                     self.config.general['gitpath'] +
                                     '\n版本信息：' +
                                     self.config.general['version'])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = YysWin()
    main_win.show()
    sys.exit(app.exec_())
