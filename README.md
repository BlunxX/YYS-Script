[TOC]

# yys自动化工具

## 写在前面

今天是 2021.1.1 ，我想这个工具是 2020 年，我最上心的一件事情。最初的时候，我只是想写一个阴阴师的辅助工具，比如用来辅助升级狗粮，樱饼不够用时也可以自动刷魂土，自动刷结界突破等等。开始的时候用 autogui 随便写了一个，偷懒脚本随机性没做好，还被鬼使黑警告了一次，因此中间弃坑了一段时间。最后舍不得好友们，重新入坑。重构脚本是在一次面试的时候被问到了设计模式，一知半解的时候看了两周的设计模式，知道为啥之前开发的脚本那么难维护了。索性重构了框架，这次是重构之后一开发记录。

先说明一下当前软件支持的功能：

![功能列表](./docs/images/ui/功能列表.jpg)

后面针对每个功能都从使用方法，注意事项，开发记录几个方面详细介绍。对于使用者，只要看对应的使用方法就可以了。

特别说明，**点击模式**是因为我在写王者荣耀自动挂血红色宫殿的时候，发现腾讯手游助手的模拟器没有办法通过脚本调节窗体大小（有开发大佬知道怎么解决可以联系我），每次都得重新截图，所以干嘛直接写一个通用的只需要匹配-解析的通用模式。最终还是拿来挂血红色宫殿。其实御灵也可以简单截几个图变成**点击模式**实现。

**本工具仅用来学习交流，请不要扩散，公平游戏环境需要大家一起维护。使用过程中如遇鬼使黑警告，封号处理本人概不负责。**

## 软件使用介绍

我按一个没有用本工具的使用者的角度，一步步按使用步骤来说明。

### 软件环境说明

- 软件环境说明，win7/win10，非4K屏显示器（之前有朋友反馈4K屏不能正常使用）

### 软件获取

gitee上不存放软件包，所以有兴趣的朋友可以直接联系我。当然做开发的朋友可以自己打包。可以加我微信（cyxqyh），添加请增加备注。

![软件文件列表](./docs/images/ui/软件文件列表.jpg)

其中 **conf 下面是配置文件**， screenshot 下面是用来匹配的截图文件， .exe 文件是可执行文件。使用时直接点击 .exe 文件即可。基本使用都也只要关心配置文件和可执行文件就可以了。

成功打开后的界面如下：

<img src="./docs/images/ui/主窗体.jpg"  width="200"  height = "300" text-align: left/>

启用一个功能的顺序：

1. 选择对应功能
2. 参数设置的那6个选项中设置对应的参数
   1. 参数获取顺序
      1. 界面设置的参数
      2. conf/config.ini 中对应功能的参数
3. 点击开始进行挑战

### 配置参数

参数在 conf 文件夹下面的 config.ini 文件中，右键用记事本打开，下图是用 notepad++ 打开。

<img src="./docs/images/ui/参数信息.jpg"/>

ini格式说明：

1. [general]，[]包含的是哪个功能配置，general是通用信息，用来设置界面
   1. title，窗口标题
   2. attention，注意事项
   3. width，height，窗体大小（不能更改）
   4. licence，认证码，用来限定认证过期时间
   5. 其他#开头的是注释说明
   6. 其他没有特别说明可能是冗余配置，没有实际作用

看[yuhun]即指御魂功能的配置信息，后面说明御魂功能的时候再介绍具体意思 

### 截图文件

screenshot 下面是按功能进行分类的对应截图，不要随意更改。如果遇到某几个界面特别不准的，可以反馈，尽量不要自己改动。

### 软件使用的技术

概括就是 图片识别 + 自动点击，当然实际还要更复杂的多。要模拟人为的识别和人为的点击，所以需要增加随机数来模拟。之前没有加随机数就被检测到使用第三方软件。目前使用几个月，都正常。

### 鬼使黑警告

**不保证绝对安全，但是已经在用了几个月，反正我自己是放心的。**

当前和好友已经用了1年多了，除了之前爬塔活动那次没加随机数，且连续半夜挂着挂了几个晚上，被警告。后续克制这种半夜挂机的反人类行为之后，都正常。

另外，点击都是用随机数，比如点击“准备”每一次都不会点击在同一个位置。程序也在使用过程中不断优化。

## 软件开发介绍

## 框架介绍

点击“开始”之后，软件跑起来的几个主要步骤：

1. config 配置解析
2. 截图文件加载
3. 设置循环前的截图对应的回调函数
4. 设置进入循环后的截图对应的回调函数
5. 循环检测
   1. 如果已经可以匹配到循环中的截图，说明可以进行循环
   2. 如果匹配到循环前的截图，执行对应的回调来处理，或点击或复杂操作，进入下一步
6. 循环后
   1. 根据通用信息 self.loop_times 决定循环执行多少次
   2. 根据对应功能特殊的配置进行各项基本操作

### 配置解析

配置的数据结构说明：

```
self.config, 所有的配置集合
self.config.general, 常规的配置，包含窗体名称之类的基础信息
self.config.yuling, 御灵功能对应的配置信息
self.config.yuhun, 御魂功能对应的配置信息
```

为了不过多得依赖配置信息，所以会在初始化功能的时候就把所有用到的配置转化成单个功能的配置，如御灵功能只用到了配置“循环次数”，“挑战类型”这两个配置。

```
class Yuling(Autogui):
    def __init__(self, win_name='阴阳师-网易游戏'):
        Autogui.__init__(self, win_name)
        # 设置当前副本的类型，设置之后优先查找御灵对应的截图
        self.screenshot.set_current_setion('yuling')  # 设置优先的截图信息
        self.config.set_current_setion('yuling')  # 设置当前配置信息
        self.pre_loop_times = self.config.cur_config.get('pre_loop_times', 20)
        self.loop_times = self.config.cur_config.get('loop_times', 20)
        self.fight_type = self.config.cur_config.get('type', 'leopard')
        self.already_select_layer = False
```

另外下面步骤也非常重要，用来设置当前优先选择的配置。尤其是图片的当前 section 必须设置。

```
self.screenshot.set_current_setion('yuling')  # 设置优先的截图信息
self.config.set_current_setion('yuling')  # 设置当前配置信息
```



目前支持的功能都是在列表中写死的。所以如果要增加一个功能时，要增加的下面几个操作：

1. config.ini 中增加类型
2. 界面的功能列表，mainwin.py 的 init_config()
3. 点击开始界面时，要显示去解析配置选项的参数 mainwin.py 的 get_config_from_param_cb()
4. 要使用对应功能来初始化  mainwin.py 的 btn_start_clicked



### 图片比对

图片比对最初用的是 autogui.locate() ，发现性能太差了，所以后面换了 opencv ，这一块有单独的调试文件，详细见 [opencv图像识别.ipynb](./单功能调试/opencv图像识别.ipynb)

比较单个图片：

```
im_yys = self.screenshot_exact()  # 获取截图
loc_tmp = self.locate_im(self.get_image(self.fight_type), im_yys) # 比对某个key是否在截图中
if loc_tmp:
    self.cur_key = self.fight_type
	self.click_loc_one(loc_tmp)
```

说到图片，还是先说下两个重要的函数： goto_loop() 和 loop()，分别对应循环前准备和进入循环。以御灵为例，两个过程中提取的关键流程如下，(key, callback) 分别对应关键 key 对应的执行函数是什么。

```
prepare_callback = [
    ('search', self.click_loc_one),
    ('yuling', self.click_loc_one),
    ('dragon', self.dragon_callback),
    ('fox', self.fox_callback),
    ('leopard', self.leopard_callback),
    ('phenix', self.phenix_callback),
]
loop_callback = [
    ('task_accept', self.task_accept_callback),
    ('fight', self.fight_callback),
    ('prepare', self.prepare_callback),
    ('victory', self.victory_callback),
    ('fail', self.fail_callback),
    ('award', self.award_callback),
]
```

然后将数据转换成对应一个中间类，如果用面向对象的思路，应该是接口，不过我这边简化掉，只存信息，不处理操作。

```
class ImageCallback():
    def __init__(self, key, image, callback):
        self.key = key
        self.image = image
        self.callback = callback
```

最终得到 (key, image, callback) 这样的关键信息的两个数组。

```
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
```



### 准备循环

准备的循环，用来确定是否可以进行循环执行。

```
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
```



### 进入循环

进行循环之后，就只会识别循环列表里面的图片。同时除非点击退出，达到循环次数，或者是异常崩溃才会退出。

```
def loop(self):
    self.cur_loop_times = 0
    while self.stop is False and self.cur_loop_times < self.loop_times:
        im_yys = self.screenshot_exact()
        found = False

        im_yys = self.screenshot_exact()  # 执行操作之后需要重新获取截图
        for callback in self.loop_image_callback:
            if callback.image is None:
                self.display_msg('请确认截图{}存在'.format(callback.key))
                continue
            loc = self.locate_im(callback.image, im_yys)
            if loc is None:
                continue
            self.cur_key = callback.key
            callback.callback(loc)  # 执行对应的回调
            time.sleep(0.5)
            found = True
            break

        if found is False:
            self.display_msg('该轮匹配不到图片')
            time.sleep(1)
```

### 界面开发

用的是 pyqt5 ，这里就不展开了，一些坑和注意事项等等后面有时间再另外写。

毕竟不是做UI的，凑合可以用就好了。

## 御灵

### 使用方法

<img src="./docs/images/yuling/御灵功能.jpg"/>

只要在符合下面两个图中状态，都是可以正常进入循环挑战。

准备循环：

<img src="./docs/images/yuling/御灵准备.gif"/>

进入循环的位置：

<img src="./docs/images/general/通用循环.gif"/>



### 注意事项

如果对应的类型没有开放的话，会自动切换类型，默认类型是豹子 -> 狐狸 -> 凤凰 -> 神龙。

### 开发记录

御灵是最简单的一个部分。

因为是第一次说明模块，所以把两个循环贴出来。

```
prepare_callback = [
	('search', self.click_loc_one),
	('yuling', self.click_loc_one),
	('unopened', self.unopened_callback),
	('dragon', self.unopened_callback),
	('fox', self.unopened_callback),
	('leopard', self.unopened_callback),
	('phenix', self.unopened_callback),
]
loop_callback = [
	('task_accept', self.task_accept_callback),
	('fight', self.fight_callback),
	('prepare', self.prepare_callback),
	('victory', self.victory_callback),
	('fail', self.fail_callback),
	('award', self.award_callback),
]
```

其中只有是**类型切换**和**挑战**是需要特别写回调的，其他都用通用的回调就可以了。

挑战是因为我们还需要切制到第三层。

```
def fight_callback(self, loc):
if self.already_select_layer is False:
	im_yys = self.screenshot_exact()
	loc_tmp = self.locate_im(self.get_image('layer3'), im_yys)
	if loc_tmp:
		self.click_loc_one(loc_tmp)
	else:
		self.display_msg('无法找到第三层：{0}'.format('layer3'))
		return
	self.already_select_layer = True
else:
	self.click_loc_one_and_move_uncover(loc)
```

类型切换的话，我们将界面选择的那个类型设置为第一个，其他的还是按照默认顺序挑战，如果挑战失败之后再进行切换下一个类型。

```
def _fighttype_callback(self, fight_type):
	im_yys = self.screenshot_exact()
	loc_tmp = self.locate_im(self.get_image(fight_type), im_yys)
	if loc_tmp:
		self.cur_key = fight_type
		self.click_loc_one(loc_tmp)
	else:
		self.display_msg('无法切换到类型：{0}'.format(fight_type))

def unopened_callback(self, loc):
	if len(self.remain_types) == 0:
		self.stop = True
		self.display_msg('所有类型都未开放')
	self.last_fight_type = self.remain_types[0]
	self.remain_types.remove(self.remain_types[0])
	self._fighttype_callback(self.last_fight_type)
```



## 御魂



## 业原火

## 结界突破

## 升级狗粮

## 困28

## 点击模式

## 常见问题及解决方法

### 无法打开界面

界面都出不来，联系我吧。

### 认证失败

<img src="./docs/images/ui/认证失败.jpg"/>

因为之前不扩散，不传播，我添加了对应的认证模式，遇到也联系我吧。

## 开发记录

