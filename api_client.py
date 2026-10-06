# -*- coding:utf-8 -*-
import json, os, sys, re, shared
from utils import asyncc

def read_persons():
    if not shared.api_key:
        print('\n× 请在 config.ini 配置 Host_API！\n')
        sys.exit()
    url = shared.host_url + 'Persons?api_key=' + shared.api_key
    try:
        rqs = shared.session.get(url=url, proxies=shared.host_proxies, timeout=60, verify=False)
        if rqs.status_code != 200:
            print(f'\n× 错误代码: {rqs.status_code}\n')
            sys.exit()
        return sorted(json.loads(rqs.text)['Items'], key=lambda x: x['Name'])
    except Exception as e:
        print(f'\n× 连接失败: {e}\n')
        sys.exit()

def get_gfriends_map():
    url = shared.repository_url + 'Filetree.json'
    if shared.repository_url == '默认/': url = 'https://raw.githubusercontent.com/gfriends/gfriends/master/Filetree.json'
    try:
        res = shared.session.get(url, timeout=30)
        if res.status_code != 200: sys.exit()
        res.encoding = 'utf-8'
        m = json.loads(res.text) if shared.aifix else json.loads(res.text.replace('AI-Fix-', ''))
        out = {}
        for s in m['Content'].keys():
            for k, v in m['Content'][s].items():
                name = k[:-4]
                if name not in out: out[name] = []
                out[name].append(url.replace('Filetree.json', f'Content/{s}/{v}'))
        return out
    except: sys.exit()

@asyncc
def download_avatar(url, actor_name, proc_md5):
    try:
        res = shared.session.get(url)
        path = f'{shared.download_path}{actor_name}.jpg'
        if res.status_code == 200:
            with open(path, 'wb') as f: f.write(res.content)
            shared.proc_log.write(proc_md5 + '\n')
    except: pass

@asyncc
def input_avatar(id, data):
    try:
        url = f'{shared.host_url}Items/{id}/Images/Primary?api_key={shared.api_key}'
        shared.session.post(url, proxies=shared.host_proxies, data=data, headers={'Content-Type': 'image/jpeg'})
    except: pass

@asyncc
def netflav_search(id, name):
    try:
        res = shared.session.get('https://netflav.com/all', params={'actress': name}, timeout=10)
        t = res.text
        
        # 兼容 Netflav 不规范的底层字段名：breast 和 hip(单数)
        bm = re.search(r'"birthday"\s*:\s*"([^"]+)"', t, re.IGNORECASE)
        cm = re.search(r'"cup"\s*:\s*"([A-Z])"', t, re.IGNORECASE)
        bust = re.search(r'"(?:bust|breast)"\s*:\s*"?(\d+)', t, re.IGNORECASE)
        waist = re.search(r'"waist"\s*:\s*"?(\d+)', t, re.IGNORECASE)
        hips = re.search(r'"hips?"\s*:\s*"?(\d+)', t, re.IGNORECASE)
        
        info = {}; tags = ['AV女优']; cup = ''; overview = ''
        
        if bm:
            info['PremiereDate'] = bm.group(1).replace('年', '-').replace('月', '-').replace('日', '').replace('.', '/').replace('/', '-')
            
        if cm:
            cup = cm.group(1).upper()
            tags.append(cup + '罩杯')
            
        b_val = bust.group(1) if bust else ''
        w_val = waist.group(1) if waist else ''
        h_val = hips.group(1) if hips else ''
        
        if b_val or w_val or h_val:
            overview = f'胸围: {b_val or "?"} cm'
            if cup: overview += f' ({cup}罩杯)'
            overview += f'\n腰围: {w_val or "?"} cm\n臀围: {h_val or "?"} cm\n'
            
        jf = './Getter/actress.json'
        with shared.json_lock:
            ad = {}
            if os.path.exists(jf):
                try:
                    with open(jf, 'r', encoding='utf-8') as f: ad = json.load(f)
                except: pass
            ad[name] = {
                'Birthday': info.get('PremiereDate', ''), 
                'Cup': cup, 
                'Bust': b_val,
                'Waist': w_val,
                'Hips': h_val
            }
            with open(jf, 'w', encoding='utf-8') as f: json.dump(ad, f, ensure_ascii=False, indent=4)
            
        dt = {'Id': id, 'Name': name, 'Overview': overview, 'Tags': tags}
        if 'PremiereDate' in info: dt['PremiereDate'] = info['PremiereDate']
        
        url_post = f'{shared.host_url}Items/{id}?api_key={shared.api_key}'
        shared.session.post(url_post, json=dt, proxies=shared.host_proxies)
        
        bp = f'B{b_val} W{w_val} H{h_val}' if (b_val or w_val or h_val) else '未知'
        print(f'\n[刮削成功] {name} - 生日:{info.get("PremiereDate", "未知")} | 罩杯:{cup} | 三围:{bp}')
    except Exception as e:
        print(f'\n[刮削失败] {name}: {e}')