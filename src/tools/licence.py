# -*- coding: utf-8 -*-
# %% 加载库

import time
import hashlib
import base64
import logging
import re
import subprocess

GENEAL_UUID = '000000000000'
GENERAL_KEY = 'kiddo'
logger = logging.getLogger('kiddo')


def execute_cmd(cmd):
    '''涉及管道，用pyinstall不能设置console=False，解决方法来自（无效）
        参考链接：https://www.2nzz.com/thread-58453-1-1.html
    '''
    proc = subprocess.Popen(cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            stdin=subprocess.PIPE)
    proc.stdin.close()
    proc.wait()
    result = proc.stdout.read().decode('gbk')  # 注意你电脑cmd的输出编码（中文是gbk）
    proc.stdout.close()
    return result


def get_machine_uuid():
    result = execute_cmd('wmic csproduct get uuid')
    result = result.replace('UUID', '')
    result = result.replace(' ', '')
    result = result.replace('\r', '')
    result = result.replace('\n', '')
    return result[-12::]


# %% 获取UUID封装成函数
# 这个库兼容性有问题，所以还是用上面的方式来取uuid
# from iupdatable.system.hardware import CSProduct
# def get_machine_uuid():
#     return CSProduct.get()["UUID"][-12::]


# %% 封装具体时间转时间戳
def transform_date_to_timestamp(year, month, day):
    time_str = '{0}-{1}-{2}'.format(year, month, day)
    data_sj = time.strptime(time_str, "%Y-%m-%d")
    return int(time.mktime(data_sj))


# %% 封装获取md5算法的函数


def get_md5(orig_str):
    m = hashlib.md5()
    m.update(orig_str.encode('utf-8'))
    return m.hexdigest()


# %% 封装生成加密串的函数和解密串的函数
def get_licence(uuid, year, month, day):
    # 先获取时间戳
    timestamp = transform_date_to_timestamp(year, month, day)

    # 获取md5
    md5 = get_md5(uuid + GENERAL_KEY)
    orig_str = '{0}_{1}'.format(md5, timestamp)

    # 获取base64编码
    encode_str = base64.b64encode(orig_str.encode('utf-8')).decode()
    logger.debug('加密用的关键信息：{0}，{1}，{2}，{3}'.format(uuid, timestamp, orig_str,
                                                   encoded_str))
    return encode_str


def check_license(encode_str):
    try:
        decode_str = base64.b64decode(encode_str.encode('utf-8')).decode()
        elements = decode_str.split('_')
        if len(elements) != 2:
            logger.debug('鉴权失败：解密串格式不对, {0}'.format(encode_str))
            return False
    except Exception:
        logger.debug('鉴权失败：解密串格式不对, {0}'.format(encode_str))
        return False

    md5, timestamp = elements[0], int(elements[1])
    logger.debug('从licence中获取到的信息：str={0}, md5={1}, time={2}'.format(
        encode_str, md5, timestamp))

    # 获取uuid，并根据关键字计算出md5
    local_md5 = get_md5(get_machine_uuid() + GENERAL_KEY)
    if md5 != local_md5:
        local_md5 = get_md5(GENEAL_UUID + GENERAL_KEY)
        if md5 != local_md5:
            logger.debug('鉴权失败：即不匹配uuid，也不匹配通用uuid,md5，{0} != {1}'.format(
                md5, local_md5))
            return False

    # 检查时间戳
    local_timestamp = int(time.time())
    if local_timestamp > timestamp:
        logger.debug('鉴权失败：timestamp，{0} < {1}'.format(timestamp,
                                                       local_timestamp))
        return False
    logger.debug(encode_str + '鉴权成功')
    return True


def get_remain_time(encode_str) -> str:
    '''不做鉴权，只校验时间，负数表示加密串异常，正数表示剩余时间'''
    decode_str = base64.b64decode(encode_str.encode('utf-8')).decode()
    elements = decode_str.split('_')
    if len(elements) != 2:
        logger.debug('鉴权失败：解密串格式不对, {0}'.format(encode_str))
        return '加密串异常'

    md5, timestamp = elements[0], int(elements[1])
    logger.debug('从licence中获取到的信息：str={0}, md5={1}, time={2}'.format(
        encode_str, md5, timestamp))

    # 检查时间戳
    local_timestamp = int(time.time())
    if local_timestamp > timestamp:
        logger.debug('鉴权失败：timestamp，{0} < {1}'.format(timestamp,
                                                       local_timestamp))
        return '加密串已经过期'
    else:
        remain_time = timestamp - local_timestamp
        if remain_time > 365 * 24 * 60 * 60:
            return '超过一年'
        elif remain_time > 24 * 60 * 60:
            days = remain_time / (24 * 60 * 60)
            return '超过{0}天'.format(int(days))
        else:
            return '还有{0}秒'.format(int(remain_time))


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    BASIC_FORMAT = '%(asctime)s - %(levelname)s: %(message)s'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)
    chlr = logging.StreamHandler()  # 输出到控制台的handler
    chlr.setFormatter(formatter)
    logger.addHandler(chlr)

    # 获取uuid
    logger.debug(get_machine_uuid())

    # 获取日期
    cur_timestamp = int(time.time())
    end_timestamp = transform_date_to_timestamp(2021, 1, 30)
    logger.debug('{0},{1}'.format(cur_timestamp, end_timestamp))

    # %% base64加密
    orig_str = '{0}-{1}'.format(get_machine_uuid(),
                                transform_date_to_timestamp(2021, 1, 30))
    encoded_str = base64.b64encode(orig_str.encode('utf-8')).decode()
    decode_str = base64.b64decode(encoded_str.encode('utf-8')).decode()
    logger.debug('{0},{1},{2}'.format(orig_str, encoded_str, decode_str))

    # md5加密
    logger.debug('{0},{1}'.format(orig_str, get_md5(orig_str)))

    # 测试鉴权结果
    licence = get_licence(get_machine_uuid(), 2020, 1, 30)
    logger.debug('检查的licence: {0}，{1}'.format(licence, check_license(licence)))

    licence = get_licence('error_uuid', 2021, 1, 30)
    logger.debug('检查的licence: {0}，{1}'.format(licence, check_license(licence)))

    licence = get_licence('14DDA9295650', 2022, 1, 1)  # 老飞的串
    logger.debug('检查的licence（老飞）: {0}，{1}'.format(licence,
                                                  check_license(licence)))

    licence = get_licence(get_machine_uuid(), 2021, 1, 30)
    logger.debug('检查的licence: {0}，{1}'.format(licence,
                                              check_license(licence)))  # 成功
    logger.debug('剩余时间{0}，{1}'.format(licence, get_remain_time(licence)))

    licence = get_licence(get_machine_uuid(), 2022, 1, 1)
    logger.debug('检查的licence: {0}，{1}'.format(licence,
                                              check_license(licence)))  # 成功
    logger.debug('剩余时间{0}，{1}'.format(licence, get_remain_time(licence)))

    licence = get_licence(GENEAL_UUID, 2021, 6, 1)
    logger.debug('检查的licence（通用一个月）: {0}，{1}'.format(
        licence, check_license(licence)))  # 成功
    logger.debug('剩余时间{0}，{1}'.format(licence, get_remain_time(licence)))
