# -*- coding:utf-8 -*-
import os, json, requests, re, time, sqlite3, argparse
from configparser import RawConfigParser

def main():
    # 1. 命令行参数解析 (使用互斥组)
    parser = argparse.ArgumentParser(description="Netflav 演员信息刮削脚本")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--data-json", action="store_true", help="保存为 actors.json (默认)")
    group.add_argument("--data-sqlite3", action="store_true", help="保存到 actors.sqlite3")
    args, _ = parser.parse_known_args()

    # 互斥逻辑：如果指定了 sqlite3，则只存 sqlite3；否则（包括指定了 json 或啥都没写）默认存 json
    save_sqlite = args.data_sqlite3
    save_json = not save_sqlite

    print(">> 正在读取 config.ini 配置文件...")
    config_file = 'config.ini'
    if not os.path.exists(config_file):
        print("× 找不到 config.ini 文件，请在项目根目录运行。")
        return

    config = RawConfigParser()
    config.read(config_file, encoding='UTF-8-SIG')
    
    try:
        host_url = config.get("媒体服务器", "Host_Url")
        api_key = config.get("媒体服务器", "Host_API")
        Proxy = config.get("下载设置", "Proxy")
    except Exception as e:
        print(f"× 读取配置失败: {e}")
        return
        
    if not host_url.endswith('/'): host_url += '/'

    # 网络与代理设置
    requests.packages.urllib3.disable_warnings()
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    if Proxy:
        session.proxies = {'http': Proxy, 'https': Proxy}

    print(f">> 正在连接 Jellyfin 服务器获取演员名单 ({host_url})...")
    try:
        url = f"{host_url}Persons?api_key={api_key}"
        res = session.get(url, timeout=60, verify=False)
        if res.status_code != 200:
            print(f"× 服务器返回错误代码: {res.status_code}")
            return
        persons = sorted(res.json().get('Items', []), key=lambda x: x['Name'])
    except Exception as e:
        print(f"× 连接 Jellyfin 服务器失败: {e}")
        return

    print(f"√ 成功获取到 {len(persons)} 位演员，准备前往 Netflav 刮削...\n")
    print(f"[*] 当前保存模式: {'SQLite3 数据库' if save_sqlite else 'JSON 文件'}")

    # 2. 存储介质初始化
    actors_data = {}
    json_file = 'actors.json'
    
    if save_json and os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                actors_data = json.load(f)
        except Exception:
            pass

    if save_sqlite:
        conn = sqlite3.connect('actors.sqlite3')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS actors (
                            name TEXT PRIMARY KEY,
                            birthday TEXT,
                            height TEXT,
                            cup TEXT,
                            bust TEXT,
                            waist TEXT,
                            hips TEXT)''')
        conn.commit()

    # 3. 开始执行刮削
    count = 0
    for p in persons:
        name = p.get('Name', '')
        if not name:
            continue
            
        search_name = re.sub(r'（.*）', '', name)
        search_name = re.sub(r'\(.*\)', '', search_name).strip()

        try:
            res = session.get('https://netflav.com/all', params={'actress': search_name}, timeout=10)
            t = res.text
            
            bm = re.search(r'"birthday"\s*:\s*"([^"]+)"', t, re.IGNORECASE)
            hm = re.search(r'"height"\s*:\s*"?(\d+)', t, re.IGNORECASE)
            cm = re.search(r'"cup"\s*:\s*"([A-Z])"', t, re.IGNORECASE)
            bust = re.search(r'"(?:bust|breast)"\s*:\s*"?(\d+)', t, re.IGNORECASE)
            waist = re.search(r'"waist"\s*:\s*"?(\d+)', t, re.IGNORECASE)
            hips = re.search(r'"hips?"\s*:\s*"?(\d+)', t, re.IGNORECASE)
            
            birthday = bm.group(1).replace('年', '-').replace('月', '-').replace('日', '').replace('.', '/').replace('/', '-') if bm else ""
            height = hm.group(1) if hm else ""
            cup = cm.group(1).upper() if cm else ""
            b_val = bust.group(1) if bust else ""
            w_val = waist.group(1) if waist else ""
            h_val = hips.group(1) if hips else ""
            
            if save_json:
                actors_data[name] = {
                    "Birthday": birthday,
                    "Height": height,
                    "Cup": cup,
                    "Bust": b_val,
                    "Waist": w_val,
                    "Hips": h_val
                }
            
            if save_sqlite:
                cursor.execute("""
                    INSERT INTO actors (name, birthday, height, cup, bust, waist, hips)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(name) DO UPDATE SET
                        birthday=excluded.birthday,
                        height=excluded.height,
                        cup=excluded.cup,
                        bust=excluded.bust,
                        waist=excluded.waist,
                        hips=excluded.hips
                """, (name, birthday, height, cup, b_val, w_val, h_val))
            
            print(f"[成功] {name:<15} | 生日:{birthday or '-':<10} | 身高:{height or '-':<3} | 罩杯:{cup or '-':<2} | 胸围:{b_val or '-':<3} | 腰围:{w_val or '-':<3} | 臀围:{h_val or '-':<3}")
            
        except Exception as e:
            print(f"[失败] {name}: 请求错误 - {e}")
            
        count += 1
        
        # 每 10 次请求执行一次磁盘 I/O 保存
        if count % 10 == 0:
            if save_json:
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(actors_data, f, ensure_ascii=False, indent=4)
            if save_sqlite:
                conn.commit()
                
        time.sleep(0.5)

    # 4. 循环结束最终保存关闭
    print("-" * 50)
    if save_json:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(actors_data, f, ensure_ascii=False, indent=4)
        print(f"√ 数据已保存至 {json_file}")
        
    if save_sqlite:
        conn.commit()
        conn.close()
        print(f"√ 数据已保存至 actors.sqlite3")
        
    print(f"√ 全部抓取完成！本次共处理 {count} 位演员。")

if __name__ == '__main__':
    main()