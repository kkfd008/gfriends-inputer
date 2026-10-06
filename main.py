# -*- coding:utf-8 -*-
import os, logging, requests, re, sys
import shared
from config import parse_args, init_config
from api_client import read_persons, get_gfriends_map
from workflow import do_download, do_upload

def main():
    conf_file, debug_flag = parse_args()
    init_config(conf_file, debug_flag)

    logging.basicConfig(filename='./Getter/logger.log', level=logging.DEBUG if shared.debug else logging.INFO)
    shared.session.mount('http://', requests.adapters.HTTPAdapter(max_retries=shared.max_retries))
    shared.session.mount('https://', requests.adapters.HTTPAdapter(max_retries=shared.max_retries))
    
    if shared.Proxy:
        shared.host_proxies = {'http': shared.Proxy, 'https': shared.Proxy}
        shared.session.proxies = shared.host_proxies
    
    persons = read_persons()
    
    # ---------------- Dry Run 强制拦截逻辑 ----------------
    if shared.dry_run > 0:
        if shared.dry_run <= len(persons):
            target = persons[shared.dry_run - 1]
            persons = [target]  # 丢弃其他人，只保留该名演员
            print(f"\n[Dry Run] 强制处理第 {shared.dry_run} 位演员: {target['Name']}")
            shared.overwrite = 1  # 强制设置为全部覆盖，保证即便服务器有头像也执行动作
            shared.Get_Intro = 1  # 强制开启信息刮削
        else:
            print(f"\n× 参数错误：--dry-run={shared.dry_run} 超出当前 Jellyfin 的演员总数 ({len(persons)})")
            sys.exit(1)
    # ---------------------------------------------------

    shared.gfriends_map = get_gfriends_map()
    shared.proc_log = open('./Getter/proc.tmp', 'a', encoding="UTF-8", buffering=1)

    for act in persons:
        name = act['Name']
        shared.actor_dict[name] = act['Id']
        
        if act.get('ImageTags'): 
            shared.exist_list.append(name)
            if not shared.overwrite: continue
                
        if not os.path.exists(shared.local_path + name + ".jpg"):
            link = shared.gfriends_map.get(name)
            if not link:
                clean_name = re.sub(r'（.*）', '', name)
                clean_name = re.sub(r'\(.*\)', '', clean_name)
                link = shared.gfriends_map.get(clean_name)
            if link:
                shared.link_dict[name] = link

    if not shared.link_dict: print("\n√ 仓库中没有需要下载的新头像。")
    else: do_download()

    for path in [shared.download_path, shared.local_path]:
        for root, _, files in os.walk(path):
            for f in files:
                if '.jpg' in f and f.replace('.jpg', '') in shared.actor_dict:
                    shared.pic_path_dict[f] = os.path.join(root, f)

    if not shared.pic_path_dict: print("\n√ 没有待导入的头像文件。")
    else: do_upload()
        
    print("\n√ 所有任务运行完毕！")

if __name__ == '__main__':
    main()