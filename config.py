# -*- coding:utf-8 -*-
import os, argparse, sys
from configparser import RawConfigParser
import shared
from utils import rewriteable_word, write_txt

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default='config.ini', nargs='?')
    parser.add_argument("-q", "--quiet", dest='quietflag', action="store_true")
    parser.add_argument("--debug", dest='debugflag', action="store_true")
    # 新增：接收 --dry-run 参数
    parser.add_argument("--dry-run", type=int, default=0, help="强制测试并处理第 N 位演员")
    
    args = parser.parse_args()
    shared.quietflag = args.quietflag
    shared.dry_run = args.dry_run # 注入共享变量
    return args.config, args.debugflag

def init_config(config_file, debugflag):
    rewriteable_word('>> 读取配置...')
    if not os.path.exists(config_file):
        content = "[媒体服务器]\nHost_Url = http://localhost:8096/\nHost_API = \n[下载设置]\nDownload_Path = ./Downloads/\nMAX_DL = 5\nMAX_Retry = 3\nRepository_Url = 默认\nAI_Fix = 是\nConflict_Proc = 0\nProxy = \n[导入设置]\nGet_Intro = 0\nLocal_Path = ./Avatar/\nOverWrite = 2\nMAX_UL = 20\nSize_Fix = 3\n[调试功能]\nDEL_ALL = 否\nDeBug = 否\nVersion = "
        write_txt("config.ini", content + shared.version)
        print('× 没有找到 config.ini。已为阁下生成，请修改后运行。\n')
        sys.exit()

    config = RawConfigParser()
    config.read('config.ini', encoding='UTF-8-SIG')
    shared.repository_url = config.get("下载设置", "Repository_Url")
    shared.host_url = config.get("媒体服务器", "Host_Url")
    shared.api_key = config.get("媒体服务器", "Host_API")
    shared.max_download_connect = config.getint("下载设置", "MAX_DL")
    shared.max_upload_connect = config.getint("导入设置", "MAX_UL")
    shared.download_path = config.get("下载设置", "Download_Path")
    shared.local_path = config.get("导入设置", "Local_Path")
    shared.fixsize = config.getint("导入设置", "Size_Fix")
    shared.Get_Intro = config.getint("导入设置", "Get_Intro")
    shared.overwrite = config.getint("导入设置", "OverWrite")
    shared.Proxy = config.get("下载设置", "Proxy")

    if not shared.host_url.endswith('/'): shared.host_url += '/'
    if not shared.repository_url.endswith('/'): shared.repository_url += '/'
    for path in ['./Getter/', shared.download_path, shared.local_path]:
        if not os.path.exists(path): os.makedirs(path)