# -*- coding:utf-8 -*-
import time, threading
from hashlib import md5
from base64 import b64encode
from alive_progress import alive_bar
import shared
from api_client import input_avatar, download_avatar, netflav_search
from image_processor import fix_size

def do_download():
    if not shared.link_dict: return
    with alive_bar(len(shared.link_dict), enrich_print=False, dual_line=True) as bar:
        for name, link in shared.link_dict.items():
            bar.text(f'正在下载：{name}')
            bar()
            p_md5 = md5((name + '+1').encode()).hexdigest()[13:-13]
            if not shared.proc_flag or p_md5 not in shared.proc_list:
                dl_link = link[0] if isinstance(link, list) else link
                download_avatar(dl_link, name, p_md5)
            while threading.active_count() > shared.max_download_connect + 1: time.sleep(0.01)
    for t in threading.enumerate():
        if t != threading.main_thread(): t.join()

def do_upload():
    if not shared.pic_path_dict: return
    if shared.fixsize:
        with alive_bar(len(shared.pic_path_dict), enrich_print=False, dual_line=True) as bar:
            for fname, path in list(shared.pic_path_dict.items()):
                bar.text(f'优化尺寸：{fname}')
                bar()
                if not fix_size(shared.fixsize, path): shared.pic_path_dict.pop(fname)

    with alive_bar(len(shared.pic_path_dict), enrich_print=False, dual_line=True) as bar:
        for fname, path in shared.pic_path_dict.items():
            name = fname.replace('.jpg', '')
            bar.text(f'推送到 Emby：{name}')
            bar()
            with open(path, 'rb') as f: data = b64encode(f.read())
            input_avatar(shared.actor_dict[name], data)
            
            # 触发信息刮削
            if shared.Get_Intro == 1:
                bar.text(f'正在刮削：{name}')
                netflav_search(shared.actor_dict[name], name)
                
            while threading.active_count() > shared.max_upload_connect + 1: time.sleep(0.01)
    for t in threading.enumerate():
        if t != threading.main_thread(): t.join()