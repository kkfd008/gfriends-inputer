# -*- coding:utf-8 -*-
import requests, logging, sys, threading

version = 'v3.04'
WINOS = True if sys.platform.startswith('win') else False
session = requests.Session()
logger = logging.getLogger()
host_proxies = None

# Config variables
repository_url = host_url = api_key = Proxy = download_path = local_path = ""
max_retries = 3; max_download_connect = 5; max_upload_connect = 20
overwrite = fixsize = Conflict_Proc = Get_Intro = 0
aifix = debug = deleteall = quietflag = updateflag = False
dry_run = 0  # 新增：Dry Run 参数
json_lock = threading.Lock() # 新增：用于 actress.json 线程安全写入

# Application State
public_ip = None
num_suc = num_fail = num_skip = num_exist = 0
exist_list = []; proc_list = []
pic_path_dict = {}; actor_dict = {}; link_dict = {}; inputed_dict = {}
gfriends_map = {}
proc_flag = False
proc_log = None