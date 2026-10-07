# -*- coding:utf-8 -*-
import os, json, requests, re, sys
import unicodedata
from configparser import RawConfigParser

def get_display_width(s):
    # 统计字符串在终端的真实显示宽度：东亚全角字符(宽字符)算 2 个宽度，半角算 1 个
    return sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in str(s))

def pad_str(s, target_width):
    # 根据显示宽度进行精准空格补齐，彻底解决中日英文混合排版错位问题
    s = str(s)
    w = get_display_width(s)
    return s + ' ' * max(0, target_width - w)

def main():
    # 1. 确定终端运行参数 (默认 verbosity = 1 即 -v)
    verbosity = 1
    if '-vvv' in sys.argv:
        verbosity = 3
    elif '-vv' in sys.argv:
        verbosity = 2
    elif '-v' in sys.argv:
        verbosity = 1

    print(">> 正在读取配置文件...")
    config_file = 'config.ini'
    if not os.path.exists(config_file):
        print("× 找不到 config.ini 文件，请在项目根目录运行。")
        return

    config = RawConfigParser()
    config.read(config_file, encoding='UTF-8-SIG')
    
    try:
        host_url = config.get("媒体服务器", "Host_Url")
        api_key = config.get("媒体服务器", "Host_API")
    except Exception as e:
        print(f"× 读取配置失败: {e}")
        return
        
    if not host_url.endswith('/'): 
        host_url += '/'

    # 抑制 SSL 警告
    requests.packages.urllib3.disable_warnings()

    print(">> 正在加载本地 actress.json 缓存数据...")
    actress_data = {}
    json_file = './Getter/actress.json'
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                actress_data = json.load(f)
        except Exception as e:
            print(f"× 加载 actress.json 失败: {e}")

    print(f">> 正在连接 Jellyfin 服务器获取底层演员数据 ({host_url})...")
    url = f"{host_url}Persons?api_key={api_key}&Fields=Overview,Tags,PremiereDate"
    
    try:
        res = requests.get(url, timeout=60, verify=False)
        if res.status_code != 200:
            print(f"× 服务器返回错误代码: {res.status_code}")
            return
        persons = sorted(res.json().get('Items', []), key=lambda x: x['Name'])
    except Exception as e:
        print(f"× 连接 Jellyfin 服务器失败: {e}")
        return

    print(f"√ 成功获取到 {len(persons)} 位演员信息。\n")

    # 2. 根据参数构造表头与分隔线
    if verbosity == 1:
        sep_len = 50
        header = pad_str("序号", 4) + " | " + pad_str("生日", 10) + " | 名字"
    elif verbosity == 2:
        sep_len = 80
        header = pad_str("编号", 32) + " | " + pad_str("序号", 4) + " | " + pad_str("生日", 10) + " | " + pad_str("罩杯", 4) + " | 名字"
    else:
        sep_len = 120
        # -vvv：编号, 序号, 生日, 罩杯, 胸围, 腰围, 臀围, 简介，名字在最后
        header = pad_str("编号", 32) + " | " + pad_str("序号", 4) + " | " + pad_str("生日", 10) + " | " + pad_str("罩杯", 4) + " | " + pad_str("胸围", 4) + " | " + pad_str("腰围", 4) + " | " + pad_str("臀围", 4) + " | " + pad_str("简介", 4) + " | 名字"

    print("=" * sep_len)
    print(header)
    print("=" * sep_len)

    # 3. 遍历并打印演员信息
    for idx_num, p in enumerate(persons, 1):
        idx = str(idx_num)
        p_id = p.get('Id', '')
        name = p.get('Name', '')
        birthday = p.get('PremiereDate', '')[:10] 
        overview = p.get('Overview', '')
        has_overview = "是" if overview else "否"

        cup, bust, waist, hips = "", "", "", ""
        
        # 解析 Jellyfin 数据库中的现有数据
        tags = p.get('Tags', [])
        for t in tags:
            if t.endswith('罩杯'): 
                cup = t.replace('罩杯', '')
                
        b_match = re.search(r'胸围:\s*(\d+)', overview)
        w_match = re.search(r'腰围:\s*(\d+)', overview)
        h_match = re.search(r'臀围:\s*(\d+)', overview)
        
        if b_match: bust = b_match.group(1)
        if w_match: waist = w_match.group(1)
        if h_match: hips = h_match.group(1)
        
        # 尝试从本地 actress.json 补充空缺数据
        if name in actress_data:
            if not cup: cup = actress_data[name].get('Cup', '')
            if not bust: bust = actress_data[name].get('Bust', '')
            if not waist: waist = actress_data[name].get('Waist', '')
            if not hips: hips = actress_data[name].get('Hips', '')

        # 补齐空值符号
        cup = cup if cup else "-"
        bust = bust if bust else "-"
        waist = waist if waist else "-"
        hips = hips if hips else "-"
        birthday = birthday if birthday else "未知"

        # 根据 verbosity 组装行数据并精准对齐
        if verbosity == 1:
            row = pad_str(idx, 4) + " | " + pad_str(birthday, 10) + " | " + name
        elif verbosity == 2:
            row = pad_str(p_id, 32) + " | " + pad_str(idx, 4) + " | " + pad_str(birthday, 10) + " | " + pad_str(cup, 4) + " | " + name
        else:
            row = pad_str(p_id, 32) + " | " + pad_str(idx, 4) + " | " + pad_str(birthday, 10) + " | " + pad_str(cup, 4) + " | " + pad_str(bust, 4) + " | " + pad_str(waist, 4) + " | " + pad_str(hips, 4) + " | " + pad_str(has_overview, 4) + " | " + name
            
        print(row)

    print("=" * sep_len)
    print(f"总计: {len(persons)} 位演员")

if __name__ == '__main__':
    main()