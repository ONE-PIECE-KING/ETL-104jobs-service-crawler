import time
import json 
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from datetime import datetime
from fake_useragent import UserAgent
import os
# import pandas as pd
import logging
from supabase import create_client, Client
# ------------------ 設定參數 -------------------
target_jobs = []
target_industry = ["研發相關類"]
target_continent = ['台灣地區']  # 若沒有設定則抓取第一個洲的所有地區
target_primary_category=[]
nouse_area = [ "澎湖縣",  "金門縣",  "連江縣" ]
nouse_district = []
nouxe_primary_category=[]
nouxe_jobs = []
# 設定 Supabase 連線參數
supabase_url: str = "https://fhvwmjlygzpczfaamecn.supabase.co"
supabase_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZodndtamx5Z3pwY3pmYWFtZWNuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDE2OTA1MTQsImV4cCI6MjA1NzI2NjUxNH0.Af8jmZdtqgosPAuyowxjWd0oM5CZniLcHiGCUZXtUDI"
# 定義目標元素的 CSS 選擇器
target_selector = 'div.job-summary'
# 定義等待超時時間（以秒為單位）
WAIT_TIMEOUT = 10
## 測試用
max_scrolls = 100000
# max_scrolls = 1
scrolls = 1
job_list = []
com_list = []
tools_list = []
applicants_analysis = []
job_url_list = []
start_time = datetime.now()
# ------------------------------------------------

"""初始化logging，預設log位址為logs/"""
def setup_logging(log_dir='logs'):
    # 確保日誌目錄存在
    os.makedirs(log_dir, exist_ok=True)
    # 產生日誌檔名（使用當前日期時間）
    log_filename = os.path.join(log_dir, f'job_crawler_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    # 創建 logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # 清除之前的 handlers（防止重複日誌）
    logger.handlers.clear()
    # 創建文件 handler
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.INFO) # 文件 handler 也只記錄 ERROR 級別訊息
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    # 創建控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO) # 控制台 handler 也只記錄 ERROR 級別訊息
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    # 添加 handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return log_filename
"""初始化driver"""
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('--start-maximized')
    # 注意要修改，偵測port可使用
    import time
import json 
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from datetime import datetime
from fake_useragent import UserAgent
import os
# import pandas as pd
import logging
from supabase import create_client, Client
import socket
# ------------------ 設定參數 -------------------
target_jobs = []
target_industry = ["研發相關類"]
target_continent = ['台灣地區']  # 若沒有設定則抓取第一個洲的所有地區
target_primary_category=[]
nouse_area = [ "澎湖縣",  "金門縣",  "連江縣" ]
nouse_district = []
nouxe_primary_category=[]
nouxe_jobs = []
# 設定 Supabase 連線參數
supabase_url: str = "https://.supabase.co"
supabase_key: str = ".."
# 定義目標元素的 CSS 選擇器
target_selector = 'div.job-summary'
# 定義等待超時時間（以秒為單位）
WAIT_TIMEOUT = 10
## 測試用
max_scrolls = 100000
# max_scrolls = 1
scrolls = 1
job_list = []
com_list = []
tools_list = []
applicants_analysis = []
job_url_list = []
start_time = datetime.now()
# ------------------------------------------------

"""初始化logging，預設log位址為logs/"""
def setup_logging(log_dir='logs'):
    # 確保日誌目錄存在
    os.makedirs(log_dir, exist_ok=True)
    # 產生日誌檔名（使用當前日期時間）
    log_filename = os.path.join(log_dir, f'job_crawler_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    # 創建 logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # 清除之前的 handlers（防止重複日誌）
    logger.handlers.clear()
    # 創建文件 handler
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.INFO) # 文件 handler 也只記錄 ERROR 級別訊息
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    # 創建控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO) # 控制台 handler 也只記錄 ERROR 級別訊息
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    # 添加 handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return log_filename
"""根據當前狀況選擇一個可用的連接埠"""
def get_available_port(start=9222, end=9322):
    """從指定範圍中尋找一個可用的連接埠"""
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                logging.info(f"找到可用的連接埠: {port}")
                return port
            except OSError:
                continue
    raise RuntimeError("沒有可用的連接埠!")
"""初始化driver"""
def setup_driver():
    available_port = get_available_port()
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('--start-maximized')
    # 注意要修改，偵測port可使用
    chrome_options.add_argument(f'--remote-debugging-port={available_port}')
    chrome_options.add_argument('--disable-gpu')
    
    ua = UserAgent()
    chrome_options.add_argument(f'user-agent={ua.random}')
    
    if os.path.exists("/usr/bin/chromium"):
        chrome_options.binary_location = "/usr/bin/chromium"
        service = Service("/usr/bin/chromedriver")
    else:
        service = Service(ChromeDriverManager().install())
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
        })
        """
    })
    driver.command_executor.set_timeout(1000)
    return driver
"""爬蟲_應徵欄位性別分布的辨識"""
def is_similar_rgb(rgb_input, target_rgb):
    """
    檢查輸入的 RGB 值（可以是字符串或列表）是否與目標 RGB 值相似。
    
    參數:
    rgb_input: 字符串 (例如 "rgb(255,144,199)") 或列表 (例如 [255,144,199])。
    target_rgb: 目標 RGB 值列表，例如 [255,144,199]。
    
    返回:
    如果相似則返回 True，否則返回 False。
    """
    # 如果傳入的是列表，則直接處理；如果是字符串則進行處理
    if isinstance(rgb_input, list):
        rgb_values = rgb_input
    elif isinstance(rgb_input, str):
        try:
            # 清除前後空格
            rgb_str = rgb_input.strip()
            # 判斷是否包含 "rgb(" 字符串，符合則提取括號內的部分
            if "rgb(" in rgb_str:
                start = rgb_str.find("rgb(") + len("rgb(")
                end = rgb_str.find(")", start)
                rgb_str = rgb_str[start:end]
            rgb_values = [int(x.strip()) for x in rgb_str.split(",")]
        except ValueError as e:
            logging.error(f"Error parsing RGB values: {e}")
            return False
    else:
        logging.error(f"Expected string or list for rgb_input, got {type(rgb_input)} instead.")
        return False
    # 設置允許的誤差範圍
    tolerance = 5
    return all(abs(a - b) <= tolerance for a, b in zip(rgb_values, target_rgb))
"""爬蟲_應徵欄位年齡的辨識"""
def extract_age_distribution(details_div):
    # 提取年齡分佈的字典
    age_distribution = {}
    
    # 找出所有的 div 元素
    data_lines = details_div.find_elements(By.CSS_SELECTOR, 'div')
    
    for line in data_lines:
        text = line.text
        # 分割文字和百分比
        parts = text.split('\n')
        
        # 確保有兩個部分（年齡範圍和百分比）
        if len(parts) == 2:
            age_range = parts[0]
            percentage = parts[1]
            
            # 將資料加入字典
            age_distribution[age_range] = percentage
    
    return age_distribution
"""爬蟲_應徵欄位工作技能、科系、技能、證照的辨識"""
def extract_experience_distribution(details_div):
    experience_distribution = {}
    
    data_lines = details_div.find_elements(By.CSS_SELECTOR, 'div')
    
    for line in data_lines:
        text = line.text
        parts = text.split('\n')
        
        if len(parts) == 2:
            experience_range = parts[0]
            percentage = parts[1]
            
            experience_distribution[experience_range] = percentage
    
    return experience_distribution
"""儲存_上傳資料到特定資料表"""
def upload_data(data, table_name = "unknown"):
    # 插入多筆資料
    try:
        if not data:
            logging.warning("無資料可上傳")
            return
        try:
            for item in data:
                try:
                    supabase.table(table_name).insert(item).execute()
                except Exception as e:
                    logging.error(f"資料上傳失敗：{e}")
                    logging.error(f"失敗的資料：{item}")
            logging.info(f"資料上傳成功")
        except Exception as e:
            logging.error(f"資料上傳失敗：{e}")
    except Exception as e:
        logging.error(f"資料上傳到 {table_name} 表失敗：{e}")
        # 額外的診斷資訊
        logging.error(f"資料範例：{data[:1]}")
        logging.error(f"資料總筆數：{len(data)}")
"""儲存_呼叫x_save()與upload_data()每多少筆存到雲端與本地"""
def x_save(data, job_count, filename = None , sum_job = 100, 
        directory='default_directory',keyword="default_keyword", table_name = "default_table_name"):
    if job_count > 0 and job_count % sum_job ==0:
        save_to_json(data, directory=directory, filename = filename)
        if table_name == 'jobs':
            upload_data(data, table_name = table_name)
        elif table_name == 'job_tools':
            logging.warning("job_tools不上傳")
        elif table_name == 'com_url':
            logging.warning("com_url不上傳")
        elif table_name == 'job_url':
            logging.warning("job_url不上傳")
        elif table_name == 'job_skills':
            logging.warning("companies 未爬蟲")
        else:
            logging.warning("table_name 未定義")
        data.clear()
        logging.info(f"已儲存 {keyword} 職缺100筆至本地與雲端")
    return data, job_count
"""儲存_存到 json"""
def save_to_json(raw_data, filename=None, mode='w', directory='default_directory'):
    """
    將職缺資料存成 JSON 檔案
    :param job_data_list: 職缺資料列表
    :param filename: 自訂檔名，預設為當前日期時間
    :param mode: 檔案寫入模式，預設為覆蓋 'w'，可選 'a' 為附加
    :param directory: 存放位置，預設為 'default_directory'
    """
    logging.info(f"正在儲存資料至 JSON 檔案...")
    # 如果未提供檔名，使用當前日期時間
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"job_details_{timestamp}.json"
    # 確保檔名以 .json 結尾
    if not filename.endswith('.json'):
        filename += '.json'
    # 確保目錄存在
    if not os.path.exists(directory):
        os.makedirs(directory)
    # 完整的檔案路徑
    file_path = os.path.join(directory, filename)
    try:
        # 檢查檔案是否已存在且模式為附加
        if mode == 'a' and os.path.exists(file_path):
            # 讀取現有的 JSON 資料
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            # 合併新舊資料
            raw_data = existing_data + raw_data
        # 使用 UTF-8 編碼寫入 JSON 檔案
        with open(file_path, mode, encoding='utf-8') as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=4)
        logging.info(f"資料已成功儲存至 {file_path}")
        return file_path
    except Exception as e:
        logging.error(f"儲存 JSON 檔案時發生錯誤: {e}")
        return None
"""爬蟲選單_點擊並等待選項展開，根據 selector 定位元素"""
def click_and_select(selector, driver):
    """点击并等待选项展开的通用函数"""
    try:
        logging.info(f"准备点击元素: {selector}")
        element = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        logging.info(f"元素已找到，准备点击")
        driver.execute_script("arguments[0].click();", element)
        logging.info(f"元素点击完成，等待动画")
        time.sleep(1)
    except TimeoutException:
        logging.error(f"等待元素超时: {selector}")
        raise
    except Exception as e:
        logging.error(f"点击元素时发生错误: {selector}, 错误: {e}")
        raise
"""爬蟲選單_選取洲別"""
def select_continent(continent_name, driver, index):
    """选择洲别"""
    try:
        logging.info(f"开始选择洲别: {continent_name}")
        # 修改: 更新选择器以匹配实际页面结构
        # 104网站实际使用的选择器可能与之前假设的不同
        continent_element = driver.find_elements(By.XPATH, '//li[contains(@class, "category-item") and contains(@class, "category-item--level-one")]')[index]

        if continent_element:
            logging.info("找到洲别元素，准备点击")
            time.sleep(1)  # 等待滚动完成
            continent_element.click()
            logging.info(f"已完成洲别选择: {continent_name}")
            time.sleep(2)  # 增加点击后的等待时间
        else:
            raise Exception(f"无法找到洲别选项: {continent_name}")
            
    except TimeoutException as te:
        logging.error(f"等待洲别元素超时: {continent_name}")
        logging.error(f"当前页面URL: {driver.current_url}")
        logging.error(f"当前页面标题: {driver.title}")
        raise
    except Exception as e:
        logging.error(f"选择洲别时发生错误: {continent_name}, 错误: {e}")
        # 添加更多调试信息
        logging.error(f"当前页面URL: {driver.current_url}")
        logging.error(f"当前页面标题: {driver.title}")
        # 尝试获取页面源码中的部分内容
        try:
            page_source = driver.page_source
            logging.error(f"页面源码片段: {page_source[:500]}...")  # 只记录前500个字符
        except:
            logging.error("无法获取页面源码")
        raise
"""爬蟲選單_選取地區"""
def select_area(area_name, driver, area_element):
    """选择地区"""
    try:
        logging.info(f"开始选择地区: {area_name}")
        area_selector = f"button.area-item[data-area='{area_name}']"
        logging.info(f"等待地区选项出现: {area_selector}")
        logging.info(f"地区选项已找到，准备点击")
        area_element.click()
        logging.info(f"已完成地区选择: {area_name}")
        time.sleep(1)
    except Exception as e:
        logging.error(f"选择地区时发生错误: {area_name}, 错误: {e}")
        raise
"""爬蟲選單_選取區"""
def select_district(district_name, driver, district_element):
    """选择地区"""
    try:
        logging.info(f"开始选择区: {district_name}")
        district_selector = f"button.area-item[data-area='{district_name}']"
        logging.info(f"等待区选项出现: {district_selector}")
        logging.info(f"地区选项已找到，准备点击")
        district_element.click()
        logging.info(f"已完成区选择: {district_name}")
        time.sleep(1)
    except Exception as e:
        logging.error(f"选择区时发生错误: {district_name}, 错误: {e}")
        raise
"""爬蟲選單_選取產業"""
def select_industry(industry_name, driver, industries_element):
    """选择产业"""
    try:
        logging.info(f"开始选择产业: {industry_name}")
        logging.info(f"产业选项已找到，准备点击")
        industries_element.click()
        logging.info(f"已完成产业选择: {industry_name}")
        time.sleep(1)
    except Exception as e:
        logging.error(f"选择产业时发生错误: {industry_name}, 错误: {e}")
        raise
"""爬蟲選單_選取次分類"""
def select_primary_category(primary_category, driver, primary_category_element):
    """选择产业"""
    try:
        logging.info(f"开始选择产业: {primary_category}")
        logging.info(f"产业选项已找到，准备点击")
        primary_category_element.click()
        logging.info(f"已完成产业选择: {primary_category}")
        time.sleep(1)
    except Exception as e:
        logging.error(f"选择产业时发生错误: {primary_category}, 错误: {e}")
        raise
"""爬蟲選單_選取職缺"""
def select_job(job_name, driver, jobs_element):
    """选择职缺"""
    try:
        logging.info(f"开始选择职缺: {job_name}")
        logging.info(f"职缺选项已找到，准备点击")
        time.sleep(3)
        driver.execute_script("arguments[0].click();", jobs_element)
        logging.info(f"已完成职缺选择: {job_name}")
        time.sleep(1)
    except Exception as e:
        logging.error(f"选择职缺时发生错误: {job_name}, 错误: {e}")
        raise
"""爬蟲選單_確認選取後進入職缺結果頁面"""
def confirm_selection(driver):
    """确认选择并进入职缺结果页面"""
    try:
        logging.info("开始确认选择")
        logging.info("等待确认按钮出现")
        confirm_element = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.category-picker-btn-primary"))
        )
        logging.info("确认按钮已找到，准备点击")
        confirm_element.click()
        logging.info("页面加载完成")
    except TimeoutException:
        logging.error("等待确认按钮或页面加载超时")
        raise
    except Exception as e:
        logging.error(f"确认选择时发生错误: {e}")
        raise
"""抓取頁面中職缺資料，返回結果列表"""
def fetch_jobs_data(driver, max_errors=3, max_scrolls=100000, area = "", district = "", industry = "", primary_category = "", job_title = ""):
    crawler_error = 0
    logging.info(f"正在處理關鍵字: {job_title}")
    try:
        # 處理職缺
        process_jobs(driver, max_scrolls, max_errors = 3, area = area, district = district, industry = industry, primary_category = primary_category, job_title = job_title)
    except Exception as e:
        crawler_error += 1
        logging.error(f"爬蟲 {job_title} 發生錯誤: {e}")
        if crawler_error >= max_errors:
            logging.warning(f"已達到最大錯誤次數 {max_errors}")
            crawler_error = 0
'''將職缺頁滑動到最後，將所有職缺詳細頁面url存取給extract_job_info使用'''
def process_jobs(driver, max_scrolls = 100000, max_errors = 3, area = "", district = "", industry = "", primary_category = "", job_title = ""):
    scrolls = 0
    current_jobs = []
    unprocessed_jobs = []
    # 滾動並收集職缺
    while True and scrolls < max_scrolls:
        logging.info(f"正在處理第 {scrolls+1} 次滾動")
        try:
            WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, target_selector))
            )
        except TimeoutException:
            logging.warning(f"等待職缺載入超時: {WAIT_TIMEOUT} 秒")
            break
        current_jobs = driver.find_elements(By.CSS_SELECTOR, target_selector)
        unprocessed_jobs = current_jobs
        current_count = len(current_jobs)
        logging.info(f"當前頁面職缺數量: {current_count}")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        scrolls += 1
        try:
            WebDriverWait(driver, WAIT_TIMEOUT).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, target_selector)) > current_count
            )
        except TimeoutException:
            logging.info("沒有新的職缺載入，可能已到底部")
            break
    # for job in current_jobs:
    ## 測試用
    logging.info(f"共找到 {len(current_jobs)} 筆職缺")
    # 該職業所有職缺主要處理循環
    remaining_jobs = current_jobs
    while remaining_jobs:
        logging.info(f"開始處理 {len(remaining_jobs)} 個職缺")
        remaining_jobs, crawler_error = extract_job_info(remaining_jobs, driver, area = area, district = district, industry = industry, primary_category = primary_category, job_title = job_title)
        if remaining_jobs:
            logging.info(f"還有 {len(remaining_jobs)} 個職缺未處理完成")
            # 儲存未處理職缺到檔案
            try:
                with open('D:/allm/crawler/undo/unprocessed_jobs.json', 'w', encoding='utf-8') as f:
                    json.dump(remaining_jobs, f, ensure_ascii=False, indent=4)
            except Exception as e:
                logging.error(f"儲存未處理職缺時發生錯誤: {e}")
            # 重置錯誤計數器，準備下一輪處理
            crawler_error = 0
            time.sleep(5)  # 短暫暫停後繼續處理
        else:
            logging.info("所有職缺處理完成")
            break
'''將詳細頁面的資料爬取'''
def extract_job_info(current_jobs, driver, max_errors = 3, crawler_error = 0, area = "", district = "", industry = "", primary_category = "", job_title = ""):
    job_count = 0
    remaining_jobs = []
    com_list = []
    job_list = []
    for job in current_jobs:
        logging.info(f"正在處理第 {job_count+1} 筆職缺")
        if crawler_error >= max_errors:
            # 將剩餘未處理的職缺加入 remaining_jobs
            remaining_jobs=(current_jobs[job_count:])
            logging.warning(f"錯誤次數達到上限 {max_errors}，暫停處理")
            crawler_error = 0
            break
        try:
            # ※關鍵修正：從目前的職缺區塊內相對查找職缺標題與網址
            title_element = job.find_element(By.XPATH, './/h2//a[contains(@class, "info-job__text")]')
            job_url = title_element.get_attribute('href')
            job_name = title_element.get_attribute('title')
            try:
                job_industry = job.find_element(By.CSS_SELECTOR, '[data-gtm-joblist^="職缺-產業-"]').text.strip()
                logging.info(f"職缺產業{job_industry}")
            except Exception as e:
                job_industry = ""
                logging.error(f"獲取職缺產業時發生錯誤: {e}")
            # 獲取公司資訊
            company_element = job.find_element(By.CSS_SELECTOR, 'a[data-gtm-joblist="職缺-公司名稱"]')
            
            company = company_element.text.strip()
            company_url = company_element.get_attribute('href')
            # 開啟新分頁取得詳細資訊
            driver.execute_script(f"window.open('{job_url}', '_blank')")
            driver.switch_to.window(driver.window_handles[-1])
            
            WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'p.job-description__content'))
            )
            # 處理詳細頁面的資訊
            try:
                logging.info(f"職缺名稱: {job_name}")
                logging.info(f"職缺網址: {job_url}")
                # 獲取更新日期，使用 title 屬性來獲取完整日期（包含年份）
                try:
                    # update_date_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'span.text-gray-darker[title*="更新"]')))
                    update_date_element = driver.find_element(By.CSS_SELECTOR, 'span.text-gray-darker[title*="更新"]')
                    update_date = update_date_element.get_attribute('title')  # 獲取完整的 title 內容
                    update_date = update_date.replace("更新", "").strip()  # 移除 "更新" 文字
                    try:
                        # 將 update_date 轉換為 datetime 物件
                        date_obj = datetime.strptime(update_date, "%Y/%m/%d")  # 假設原始格式為 YYYY/MM/DD
                        # 格式化為 YYYY-MM-DD
                        update_date = date_obj.strftime("%Y-%m-%d")
                        logging.info(f"更新日期: {update_date}")
                    except ValueError as e:
                        # 如果日期格式不匹配，捕捉錯誤
                        logging.error(f"日期轉換失敗: {e}. 原始日期: {update_date}")
                except Exception as e:
                    update_date = "N/A"
                    logging.error(f"獲取更新日期時發生錯誤: {e}")
                    logging.info("無法獲取更新日期")
                # 檢查是否為積極徵才中（可能不存在）
                try:
                    actively_hiring = driver.find_element(By.CSS_SELECTOR, 'div.actively-hiring-tag').text.strip()
                    actively_hiring = True if actively_hiring == "積極徵才中" else False
                except:
                    actively_hiring = False
                # 獲取應徵人數
                applicants = driver.find_element(By.CSS_SELECTOR, 'a.d-flex.align-items-center.font-weight-bold').text.strip()
                # 提取數字範圍（例如："應徵人數 0~5 人" -> "0~5"）
                if applicants:
                    applicants = applicants.replace("應徵人數", "").replace("人", "").strip()
                else:
                    applicants = ""
                    logging.info(f"獲取應徵人數時發生錯誤: {e}")
                try:
                    # 獲取工作內容
                    job_description = driver.find_element(By.CSS_SELECTOR, 'p.job-description__content').text.strip()
                except Exception as e:
                    job_description = ""
                    logging.error(f"獲取工作內容時發生錯誤: {e}")
                try:
                    # 獲取職務類別
                    job_categories = driver.find_elements(By.CSS_SELECTOR, 'div.category-item u')
                    job_category = '、'.join([cat.text for cat in job_categories])
                except Exception as e:
                    job_category = ""
                    logging.error(f"獲取職務類別時發生錯誤: {e}")
                try:
                    # 獲取工作待遇
                    salary = driver.find_element(By.CSS_SELECTOR, 'p.text-primary.font-weight-bold').text.strip()
                except Exception as e:
                    salary = ""
                    logging.error(f"獲取工作待遇時發生錯誤: {e}")
                try:
                    # 獲取工作性質
                    job_type = driver.find_element(By.CSS_SELECTOR, 'div.list-row:nth-child(4) div.list-row__data').text.strip()
                except Exception as e:
                    job_type = ""
                    logging.error(f"獲取工作性質時發生錯誤: {e}")
                try:
                    # 獲取上班地點
                    location = driver.find_element(By.CSS_SELECTOR, 'div.job-address span').text.strip()
                except Exception as e:
                    location = ""
                    logging.error(f"獲取上班地點時發生錯誤: {e}")
                try:
                    # 獲取管理責任
                    management_elements = driver.find_elements(By.CSS_SELECTOR, 'div.list-row')
                    management = ""
                    for element in management_elements:
                        try:
                            title_text = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title_text == "管理責任":
                                management = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                                break
                        except Exception as e:
                            logging.error(f"獲取管理責任時發生錯誤: {e}")
                            continue
                except Exception as e:
                    management = ""
                    logging.error(f"獲取管理責任時發生錯誤: {e}")
                try:
                    # 獲取出差外派
                    business_trip = ""
                    for element in management_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "出差外派":
                                business_trip = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                                break
                        except Exception as e:
                            logging.error(f"獲取出差外派時發生錯誤: {e}")
                            continue
                    # 獲取上班時段
                    work_time = ""
                    for element in management_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "上班時段":
                                work_time = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                                break
                        except Exception as e:
                            logging.error(f"獲取上班時段時發生錯誤: {e}")
                            continue
                    # 獲取休假制度
                    vacation = ""
                    for element in management_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "休假制度":
                                vacation = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                                break
                        except Exception as e:
                            logging.error(f"獲取休假制度時發生錯誤: {e}")
                            continue
                    # 獲取可上班日
                    start_work = ""
                    for element in management_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "可上班日":
                                start_work = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                                break
                        except Exception as e:
                            logging.error(f"獲取可上班日時發生錯誤: {e}")
                            continue
                    # 獲取需求人數
                    headcount = ""
                    for element in management_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "需求人數":
                                headcount = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                                break
                        except Exception as e:
                            logging.error(f"獲取需求人數時發生錯誤: {e}")
                            continue
                except Exception as e:
                    business_trip = ""
                    work_time = ""
                    vacation = ""
                    start_work = ""
                    headcount = ""
                    logging.error(f"獲取工作條件時發生錯誤: {e}")
                # 獲取工作經歷
                work_exp = ""
                work_exp_elements = driver.find_elements(By.CSS_SELECTOR, 'div.list-row')
                try:
                    for element in work_exp_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "工作經歷":
                                work_exp = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                                break
                        except Exception as e:
                            logging.error(f"獲取工作經歷時發生錯誤: {e}")
                            continue
                    # 獲取學歷要求
                    education = ""
                    for element in work_exp_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "學歷要求":
                                education = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                                break
                        except Exception as e:
                            logging.error(f"獲取學歷要求時發生錯誤: {e}")
                            continue
                    # 獲取科系要求
                    major = ""
                    for element in work_exp_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "科系要求":
                                major = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                                break
                        except Exception as e:
                            logging.error(f"獲取科系要求時發生錯誤: {e}")
                            continue
                    # 獲取語文條件
                    language = ""
                    for element in work_exp_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "語文條件":
                                language = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                                break
                        except Exception as e:
                            logging.error(f"獲取語文條件時發生錯誤: {e}")
                            continue
                    # 獲取擅長工具
                    tools = ""
                    for element in work_exp_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "擅長工具":
                                tools_elements = element.find_elements(By.CSS_SELECTOR, 'div.list-row__data u')
                                tools = '、'.join([tool.text for tool in tools_elements])
                                break
                        except Exception as e:
                            logging.error(f"獲取擅長工具時發生錯誤: {e}")
                            continue
                    # 獲取工作技能
                    skills = ""
                    for element in work_exp_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "工作技能":
                                skills_elements = element.find_elements(By.CSS_SELECTOR, 'div.list-row__data u')
                                skills = '、'.join([skill.text for skill in skills_elements])
                                break
                        except Exception as e:
                            logging.error(f"獲取工作技能時發生錯誤: {e}")
                            continue
                    # 獲取具備證照
                    certificates = ""
                    for element in work_exp_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "具備證照":
                                cert_elements = element.find_elements(By.CSS_SELECTOR, 'div.list-row__data u')
                                certificates = '、'.join([cert.text for cert in cert_elements])
                                break
                        except Exception as e:
                            logging.error(f"獲取具備證照時發生錯誤: {e}")
                            continue
                    # 獲取其他條件
                    other_requirements = ""
                    for element in work_exp_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "其他條件":
                                other_requirements = element.find_element(By.CSS_SELECTOR, 'div.list-row__data p.r3').text.strip()
                                break
                        except Exception as e:
                            logging.info("其他條件無資訊")
                            continue
                except Exception as e:
                    work_exp = ""
                    education = ""
                    major = ""
                    language = ""
                    tools = ""
                    skills = ""
                    certificates = ""
                    other_requirements = ""
                    logging.error(f"獲取工作條件時發生錯誤: {e}")
                # 獲取福利制度
                # 法定項目
                legal_benefits = []
                legal_elements = driver.find_elements(By.CSS_SELECTOR, 'div.benefits-labels:nth-child(3) span.tag--text a')
                if legal_elements: 
                    legal_benefits = [item.text.strip() for item in legal_elements]
                    legal_benefits_str = '、'.join(legal_benefits)
                else:
                    logging.info("法定項目無資訊")
                    legal_benefits_str = ""
                # 其他福利
                other_benefits = []
                other_elements = driver.find_elements(By.CSS_SELECTOR, 'div.benefits-labels:nth-child(5) span.tag--text a')
                if other_elements:
                    other_benefits = [item.text.strip() for item in other_elements]
                    other_benefits_str = '、'.join(other_benefits)
                else:
                    logging.info("其他福利無資訊")
                    other_benefits_str = ""
                # 未整理的福利說明
                raw_benefits = ""
                benefits_description = driver.find_element(By.CSS_SELECTOR, 'div.benefits-description p.r3')
                if benefits_description:
                    raw_benefits = benefits_description.text.strip()     
                else:
                    logging.info("未整理的福利說明無資訊")
                    raw_benefits = ""
                # 獲取聯絡方式
                contact_info = []
                contact_elements = driver.find_elements(By.CSS_SELECTOR, 'div.job-contact-table div.job-contact-table__data')
                if contact_elements:
                    contact_info = [element.text.strip() for element in contact_elements]
                    contact_info_str = '\n'.join(contact_info)
                else:
                    logging.info("聯絡方式無資訊")
                    contact_info_str = ""     
                try:
                    logging.info("開始開啟應徵分頁")
                    # 開啟應徵分頁獲取詳細資訊
                    # 從原始工作頁面 URL 提取工作代碼
                    apply_code = job_url.split('/')[-1].split('?')[0]
                    # 構建應徵分析頁面的 URL
                    try:
                        apply_analysis_url = f"https://www.104.com.tw/jobs/apply/analysis/{apply_code}"
                        driver.execute_script(f"window.open('{apply_analysis_url}', '_blank')")
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(5)
                    except Exception as e:
                        logging.error(f"分析與開啟應徵分析頁面代碼發生錯誤: {e}")
                    # 抓取教育程度分布
                    apply_education = {}
                    education_elements = driver.find_elements(By.CSS_SELECTOR, "div.legend__text")
                    education_values = driver.find_elements(By.CSS_SELECTOR, "div.legend__value") 
                    try:
                        for i in range(len(education_elements)):
                            apply_education[education_elements[i].text] = education_values[i].text
                    except Exception as e:
                        apply_education = {}
                        logging.info("教育程度分佈無資料")
                    # 抓取性別分布
                    gender = {"男性":"", "女性":""}
                    gender_elements = driver.find_elements(By.CSS_SELECTOR, ".stack-bar__text__block")
                    if gender_elements:
                        for element in gender_elements[:2]:
                            style = element.get_attribute("style")
                            if "rgb" in style:
                                rgb_value = style[style.find("rgb"):style.find(")") + 1]
                                rgb_value = rgb_value.strip()
                                rgb_value = rgb_value.replace("rgb(", "").replace(")", "")
                                rgb_value = [int(x) for x in rgb_value.split(",")]
                                gender_text = element.find_element(By.CSS_SELECTOR, "div").text
                                male_rgb = [78, 145, 255]    # 藍色
                                female_rgb = [255, 144, 199]  # 粉色
                                if is_similar_rgb(rgb_value, male_rgb):
                                    gender["男性"] = gender_text
                                elif is_similar_rgb(rgb_value, female_rgb):
                                    gender["女性"] = gender_text
                    else:
                        gender = {}
                        logging.info("性別分佈無資料")
                    # 抓取語言能力
                    # 選取div.chart-container__body的第5個是下下之策
                    # language_container = driver.find_elements(By.CSS_SELECTOR, "div.chart-container__body")[5]
                    logging.info("開始抓取語言能力")
                    language_containers = driver.find_elements(By.CSS_SELECTOR, "div.chart-container__body")
                    if len(language_containers) > 5:
                        language_container = language_containers[5]
                        # 初始化語言能力字典
                        language_skills = {}
                        # 找出所有語言項目
                        language_items = language_container.find_elements(By.XPATH, ".//div[contains(@class, 'mb-4')]")
                        for language_item in language_items:
                            # 提取語言名稱
                            language_name = language_item.find_element(By.XPATH, ".//span[contains(@class, 'text-truncate')]").text
                            # 找出該語言的技能等級和百分比
                            skill_bars = language_item.find_elements(By.XPATH, ".//div[contains(@class, 'stack-bar__text__block')]")
                            # 建立該語言的技能描述
                            language_description = []
                            # 圖例映射
                            legend_map = {
                                "rgb(255, 231, 217)": "不會",
                                "rgb(255, 213, 189)": "略懂",
                                "rgb(255, 195, 161)": "中等",
                                "rgb(204, 156, 129)": "精通"
                            }
                            for bar in skill_bars:
                                try:
                                    percentage = bar.text
                                    # 獲取背景顏色
                                    background_color = bar.get_attribute('style').split('background:')[1].split(';')[0].strip()
                                    skill_level = legend_map.get(background_color, "未知")
                                    language_description.append(f"{skill_level}{percentage}")
                                except Exception as e:
                                    logging.info("語言技能分佈無資料")
                            # 將語言技能加入字典
                            language_skills[language_name] = ','.join(language_description)                        
                    else:
                        logging.error("語言能力容器數量不足")
                    # 定位所有的圖表容器
                    chart_containers = driver.find_elements(By.CSS_SELECTOR, 'div.chart-container.d-flex.flex-column.bg-white.overflow-hidden.horizontal-bar-chart')
                    if chart_containers:
                        # 欄位名稱列表
                        fields = {
                            '年齡': extract_age_distribution,
                            '工作經驗': extract_experience_distribution,
                            '科系': extract_experience_distribution,  # 可以重複使用
                            '技能': extract_experience_distribution,
                            '證照': extract_experience_distribution
                        }
                        # 遍歷每個圖表容器
                        for container in chart_containers:
                            # 找出標題 DIV
                            title_div = container.find_element(By.CSS_SELECTOR, 'div:first-child')
                            # 找出詳細資訊 DIV
                            details_div = container.find_element(By.CSS_SELECTOR, 'div:last-child')
                            # 獲取標題
                            title = title_div.text
                            # 根據標題提取資料
                            if title in fields:
                                # 使用對應的提取方法
                                extraction_method = fields[title]
                                extracted_data = extraction_method(details_div)
                                # 根據標題存儲到對應的變數
                                if title == '年齡':
                                    try:
                                        age_distribution = extracted_data
                                    except Exception as e:
                                        logging.info("年齡分佈無資料")
                                        age_distribution = {}
                                elif title == '工作經驗':
                                    try:
                                        work_experience = extracted_data
                                    except Exception as e:
                                        logging.info("工作經驗分佈無資料")
                                        work_experience = {}
                                elif title == '科系':
                                    try:
                                        major_distribution = extracted_data
                                    except Exception as e:
                                        logging.info("科系分佈無資料")
                                        major_distribution = {}
                                elif title == '技能':
                                    try:
                                        skills_distribution = extracted_data
                                    except Exception as e:
                                        logging.info("技能分佈無資料")
                                        skills_distribution = {}
                                elif title == '證照':
                                    try:
                                        certificates_distribution = extracted_data
                                    except Exception as e:
                                        logging.info("證照分佈無資料")
                                        certificates_distribution = {}
                                else:
                                    logging.info(f"未知的標題: {title}")
                            else:
                                logging.info(f"未知的標題: {title}")
                    else:
                        logging.error("應徵眾多資訊無資訊")
                    # 關閉應徵頁面，切回列表頁
                    driver.close()
                    driver.switch_to.window(driver.window_handles[-1])
                except Exception as e:
                    # 關閉應徵頁面，切回列表頁
                    driver.close()
                    driver.switch_to.window(driver.window_handles[-1])
                    logging.error(f"獲取應徵詳細資訊時發生錯誤: {e}")
                    apply_education, gender, language_skills, age_distribution, work_experience, major_distribution, skills_distribution, certificates_distribution = {}
                "apply_education"=={} 
                "apply_gender"== {}
                "apply_language"== {}
                "apply_age_distribution"== {}
                "apply_experience"== {}
                "apply_major"== {}
                "apply_skills"== {}
                "apply_certificates"== {}                      
                time.sleep(3)
                # 更新要存入的資料
                logging.info(f"更新要存入的資料")
                try:
                    parts = company_url.split('/')
                    if len(parts) >= 5:
                        # 以下假設 URL 格式為 "https://www.104.com.tw/company/ID?..."
                        company_id = parts[4].split('?')[0]
                        com_list.append({"company_url":company_url, "company_id":company_id})  
                    else:
                        com_list.append({"company_url":"", "company_id":""})
                        raise ValueError("URL 格式錯誤: " + company_url)
                except Exception as e:
                    logging.error(f"處理公司網址時發生錯誤: {e}")
                try:
                    job_list.append({
                        "job_id":apply_code+update_date,
                        "job_name":job_name, "job_industry":job_industry, "area":area+district, "industry": industry, "primary_category":primary_category, 
                        "job_title":job_title,"company_name":company, "update_date":update_date, "actively_hiring":actively_hiring, 
                        "applicants":applicants, "job_description":job_description, "job_category":job_category, "salary":salary, "job_type":job_type, 
                        "location":location, "management":management, "business_trip":business_trip, "work_time":work_time, "vacation":vacation, 
                        "start_work":start_work, "headcount":headcount, "work_exp":work_exp, "education":education, "major":major, 
                        "language":language, "skills":skills, "tools": tools, "certificates":certificates, "other_requirements":other_requirements,
                        "legal_benefits":legal_benefits_str, "other_benefits":other_benefits_str, "raw_benefits":raw_benefits, "contact_info":contact_info_str,
                        "apply_education":apply_education, "apply_gender": gender, "apply_language": language_skills, "apply_age_distribution": age_distribution,
                        "apply_experience": work_experience, "apply_major": major_distribution, "apply_skills": skills_distribution, "apply_certificates": certificates_distribution,
                        "status": "active"                     
                    })
                except Exception as e:
                    logging.error(f"處理職缺時發生錯誤: {e}")

                job_count+=1
            except Exception as e:
                logging.error(f"處理詳細頁面資訊時發生錯誤: {e}")
                job_list.append({
                    "job_id":apply_code+update_date,
                    "job_name":job_name, "job_industry":job_industry, "area":area+district, "industry": industry, "primary_category":primary_category, 
                    "job_title":job_title,"company_name":company, "update_date":update_date, "actively_hiring":actively_hiring, 
                    "applicants":"", "job_description": "", "job_category": "", "salary": "", "job_type": "",
                    "location": "", "management": "", "business_trip": "", "work_time": "",
                    "vacation": "", "start_work": "", "headcount": "", "work_exp": "", "education": "", 
                    "major":"", "language":"", "skills":"", "tools":"", "certificates":"", 
                    "other_requirements":"", "legal_benefits":"", "other_benefits":"", "raw_benefits":"", "contact_info":"", "status": "draft",
                    "apply_education":{}, "apply_gender": {}, "apply_language": {}, "apply_age_distribution": {},
                    "apply_experience": {}, "apply_major": {}, "apply_skills": {}, "apply_certificates": {}
                    # 新增欄位的空值
                })             
                com_list.append({"company_url":"", "company_id":""})
                job_count +=1
                # if sum(1 for field in job_list[-1] if field == "") > 6:
                #     crawler_error += 1
                #     logging.info("職缺超過六個空缺")
            # 關閉詳細頁面，切回列表頁
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            # 儲存資料
            try:
                job_list_count = len(job_list)
                logging.info(f"目前第{job_list_count}個職缺，儲存資料")
                x_save(job_list, job_count= job_list_count,directory='D:/allm/crawler/job_list',keyword = "job_list", table_name='jobs')
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"com_url_{timestamp}.json"
                x_save(com_list, job_count= job_list_count,filename = filename ,directory='D:/allm/crawler/com_url', keyword="com_url", table_name="com_url")
            except Exception as e:
                logging.error(f"儲存時發生錯誤: {e}")
        except Exception as e:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            logging.error(f"處理職缺時發生錯誤: {e}")
            crawler_error += 1
    if len(job_list)>0:
        # job_list_count = len(job_list)
        # logging.info(f"目前第{job_list_count}個職缺，儲存資料")
        # x_save(job_list, job_count= job_list_count,directory='D:/allm/crawler/job_list',keyword = "job_list", table_name='jobs')
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # filename = f"com_url_{timestamp}.json"
        # x_save(com_list, job_count= job_list_count,filename = filename ,directory='D:/allm/crawler/com_url', keyword="com_url", table_name="com_url")
        # def upload_data(data, table_name = "unknown"):
        # def save_to_json(raw_data, filename=None, mode='w', directory='default_directory'):
        save_to_json(job_list, directory='D:/allm/crawler/job_list')
        upload_data(job_list, table_name='jobs')
        job_list = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"com_url_{timestamp}.json"
        save_to_json(com_list,filename = filename , directory='D:/allm/crawler/com_url')
        com_list = []
    return remaining_jobs, crawler_error
def crawl():
    logging.info("开始爬取程序")
    driver = setup_driver()
    logging.info("浏览器驱动初始化完成")
    base_url = "https://www.104.com.tw/jobs/search"
    logging.info(f"准备访问网站: {base_url}")
    driver.get(base_url)
    logging.info("网站加载完成")
    # 等待并点击地区按钮
    logging.info("等待地区按钮出现...")
    area_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-gtm-joblist='搜尋欄位-地區']")))
    area_button.click()
    # 洲别选取
    logging.info("开始处理洲别选择")
    try:
        continents_to_iterate = target_continent if target_continent else []
    except Exception as e:
        logging.error(f"處理洲別時發生錯誤1: {e}")
    try:
        time.sleep(3)
        continent_elements = driver.find_elements(By.XPATH, '//li[contains(@class, "category-item") and contains(@class, "category-item--level-one")]')
        # category-item category-item--focus category-item--level-one
    except Exception as e:
        logging.error(f"處理洲別時發生錯誤2: {e}")
    try:
        continent_texts = [element.text for element in continent_elements]
    except Exception as e:
        logging.error(f"處理洲別時發生錯誤3: {e}")   
    logging.info(continent_texts)
    if not continents_to_iterate:
        logging.info("未指定目标洲别，将选取所有洲别")
        continent_elements = driver.find_elements(By.XPATH, '//li[contains(@class, "category-item") and contains(@class, "category-item--level-one")]')
        continents_to_iterate = [elem.text for elem in continent_elements]
        logging.info(f"找到以下洲别: {continents_to_iterate}")
    con_select_count = 0
    for continent in continents_to_iterate:
        logging.info(f"=== 开始处理洲别: {continent} ===")
        continent_index = continent_texts.index(continent)
        if con_select_count != 0:
            area_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-gtm-joblist='搜尋欄位-地區']")))
            area_button.click()            
        select_continent(continent, driver, continent_index)
        # 地区选取
        logging.info("开始处理縣市选择")
        area_elements = driver.find_elements(By.XPATH, f'//li[contains(@class, "category-item") and contains(@class, "category-item--level-two")]')
        area_texts = [a.text for a in area_elements if a.text not in nouse_area]
        logging.info(f"找到以下可用縣市: {area_texts}")
        area_select_count = 0
        for area in area_texts:
            logging.info(f"=== 开始处理縣市: {area} ===")
            area_index = area_texts.index(area)
            area_element = area_elements[area_index]
            if area_select_count != 0:
                area_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-gtm-joblist='搜尋欄位-地區']")))
                area_button.click()
                select_continent(continent, driver, continent_index)                
            select_area(area, driver, area_element)
            # 區 選取
            logging.info("开始处理行政區選擇")
            district_elements = driver.find_elements(By.XPATH, f'//li[contains(@class, "category-item") and contains(@class, "category-item--level-three")]')
            district_texts = [a.text for a in district_elements if a.text != "" and a.text not in nouse_district]
            logging.info(f"找到以下可用行政區: {district_texts}")
            dis_select_count = 0
            for district in district_texts:
                logging.info(f"=== 开始处理行政區: {district} ===")
                district_index = district_texts.index(district)
                district_element = district_elements[district_index]
                if dis_select_count != 0:
                    area_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-gtm-joblist='搜尋欄位-地區']")))
                    area_button.click()
                    select_continent(continent, driver, continent_index)
                    select_area(area, driver, area_element)                    
                select_district(district, driver, district_element)
                confirm_selection(driver)
                # 产业选取
                logging.info("开始处理产业选择")
                try:
                    industries_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-gtm-joblist='搜尋欄位-職類']")))
                    industries_button.click()
                except Exception as e:
                    logging.error(f"產業案件錯誤{e}")
                time.sleep(3)
                industries_to_iterate = target_industry if target_industry else []
                # 所有產業的網頁元素
                industries_elements = driver.find_elements(By.XPATH, '//li[contains(@class, "category-item") and contains(@class, "category-item--level-one")]')
                # 所有產業的文字
                industries_texts = [element.text for element in industries_elements]
                logging.info(industries_texts)
                if not industries_to_iterate:
                    logging.info("未指定目标产业，将选取全部产业")
                    industries_to_iterate = industries_texts
                    logging.info(f"选择的产业: {industries_to_iterate}")
                ind_select_count = 0
                for industry in industries_to_iterate:
                    logging.info(f"=== 开始处理产业: {industry} ===")
                    indus_index = industries_texts.index(industry)
                    industries_element = industries_elements[indus_index]
                    if ind_select_count != 0:
                        try:
                            industries_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-gtm-joblist='搜尋欄位-職類']")))
                            industries_button.click()
                        except Exception as e:
                            logging.error(f"產業按鍵錯誤: {e}")
                    select_industry(industry, driver, industries_element)
                    # 次要職業分類选取
                    primary_category_to_iterate = target_primary_category if target_primary_category else []
                    primary_category_elements = driver.find_elements(By.XPATH, '//li[contains(@class, "category-item") and contains(@class, "category-item--level-two")]')
                    primary_category_texts = [a.text for a in primary_category_elements if a.text not in nouxe_primary_category]
                    logging.info(f"找到以下可用次分類: {primary_category_texts}")
                    logging.info("开始处理次要职缺选择")
                    if not primary_category_to_iterate:
                        logging.info("未指定目标次分類，将选取全部次分類")
                        primary_category_to_iterate = primary_category_texts
                        logging.info(f"选择的次分類:{primary_category_to_iterate}")
                    pc_select_count = 0
                    for primary_category in primary_category_to_iterate:
                        logging.info(f"=== 开始处理次分類: {primary_category} ===")
                        prim_index = primary_category_texts.index(primary_category)
                        primary_category_element = primary_category_elements[prim_index]
                        if pc_select_count ==0:
                            select_primary_category(primary_category, driver, primary_category_element)
                        else:
                            try:
                                industries_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-gtm-joblist='搜尋欄位-職類']")))
                                industries_button.click()
                            except Exception as e:
                                logging.error(f"產業按鍵錯誤{e}")                            
                            select_primary_category(primary_category, driver, primary_category_element)
                        # 職業選取
                        jobs_to_iterate = target_jobs if target_jobs else []
                        jobs_elements = driver.find_elements(By.XPATH, '//li[contains(@class, "category-item") and contains(@class, "category-item--level-three")]')
                        jobs_texts = [a.text for a in jobs_elements if a not in nouxe_jobs]
                        logging.info("开始处理職務选择")
                        if not jobs_to_iterate:
                            logging.info("未指定目标職務，将选取全部職業")
                            jobs_to_iterate = jobs_texts
                        jobs_count=0
                        logging.info(f"选择的職務: {jobs_to_iterate}")
                        jobs_to_iterate = [item for item in jobs_to_iterate if item != '']
                        logging.info(f"选择的職務: {jobs_to_iterate}")
                        for job_title in jobs_to_iterate:
                            logging.info(f"=== 开始处理職務: {job_title} ===")
                            job_index = jobs_texts.index(job_title)
                            ex_job_index = jobs_texts.index(job_title) -1
                            jobs_element = jobs_elements[job_index]
                            ex_jobs_element = jobs_elements[ex_job_index]
                            if jobs_count ==0:
                                select_job(job_title, driver, jobs_element)
                                confirm_selection(driver)
                                confirm_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-gtm-joblist='搜尋欄位-搜尋點擊']")))
                                logging.info("确认按钮已找到，准备点击")
                                confirm_element.click()
                                logging.info("开始获取职缺数据")
                                fetch_jobs_data(driver, max_errors=3, max_scrolls=10000, area = area, district = district, industry = industry, primary_category = primary_category, job_title = job_title)
                                logging.info(f"完成职缺 {job_title} 的数据获取")                               
                            else:
                                try:
                                    industries_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-gtm-joblist='搜尋欄位-職類']")))
                                    industries_button.click()
                                except Exception as e:
                                    logging.error(f"產業案件錯誤{e}")
                                select_job(job_title, driver, jobs_element)
                                confirm_selection(driver)
                                confirm_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-gtm-joblist='搜尋欄位-搜尋點擊']")))
                                logging.info("确认按钮已找到，准备点击")
                                confirm_element.click()
                                logging.info("开始获取职缺数据")
                                fetch_jobs_data(driver, max_errors=3, max_scrolls=10000, area = area, district = district, industry = industry, primary_category = primary_category, job_title = job_title)
                                logging.info(f"完成职缺 {job_title} 的数据获取")                                                      
                            try:
                                industries_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-gtm-joblist='搜尋欄位-職類']")))
                                industries_button.click()
                            except Exception as e:
                                logging.error(f"產業按鍵錯誤{e}")
                            select_job(job_title, driver, jobs_element)
                            confirm_selection(driver)                            
                            jobs_count +=1
                        pc_select_count += 1
                industries_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-gtm-joblist='搜尋欄位-職類']")))
                industries_button.click()                
                dis_select_count += 1
                select_district(district, driver, district_element)
                confirm_selection(driver)
            area_select_count += 1           
        con_select_count +=1
    logging.info("所有数据爬取完成")
    driver.quit()
    logging.info("浏览器已关闭，程序结束")
if __name__ == "__main__":
    log_file = setup_logging()
    logging.info(f"日誌檔案已建立：{log_file}")
    # 建立 Supabase 客戶端
    supabase: Client = create_client(supabase_url, supabase_key)
    # 建立 為執行職缺暫存資料夾
    os.makedirs('D:/allm/crawler/undo', exist_ok=True)
    crawl()
    if len(job_list) > 0:
        x_save(job_list, job_count= 2,directory='D:/allm/crawler/job_list', table_name='jobs')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        x_save(com_list, job_count= 2,filename = f"com_url_{timestamp}.json" ,directory='D:/allm/crawler/com_url', table_name="com_url")
    logging.info("職缺爬蟲程式執行完畢")



    chrome_options.add_argument('--disable-gpu')
    
    ua = UserAgent()
    chrome_options.add_argument(f'user-agent={ua.random}')
    
    if os.path.exists("/usr/bin/chromium"):
        chrome_options.binary_location = "/usr/bin/chromium"
        service = Service("/usr/bin/chromedriver")
    else:
        service = Service(ChromeDriverManager().install())
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
        })
        """
    })
    driver.command_executor.set_timeout(1000)
    return driver
"""爬蟲_應徵欄位性別分布的辨識"""
def is_similar_rgb(rgb_input, target_rgb):
    """
    檢查輸入的 RGB 值（可以是字符串或列表）是否與目標 RGB 值相似。
    
    參數:
    rgb_input: 字符串 (例如 "rgb(255,144,199)") 或列表 (例如 [255,144,199])。
    target_rgb: 目標 RGB 值列表，例如 [255,144,199]。
    
    返回:
    如果相似則返回 True，否則返回 False。
    """
    # 如果傳入的是列表，則直接處理；如果是字符串則進行處理
    if isinstance(rgb_input, list):
        rgb_values = rgb_input
    elif isinstance(rgb_input, str):
        try:
            # 清除前後空格
            rgb_str = rgb_input.strip()
            # 判斷是否包含 "rgb(" 字符串，符合則提取括號內的部分
            if "rgb(" in rgb_str:
                start = rgb_str.find("rgb(") + len("rgb(")
                end = rgb_str.find(")", start)
                rgb_str = rgb_str[start:end]
            rgb_values = [int(x.strip()) for x in rgb_str.split(",")]
        except ValueError as e:
            logging.error(f"Error parsing RGB values: {e}")
            return False
    else:
        logging.error(f"Expected string or list for rgb_input, got {type(rgb_input)} instead.")
        return False
    # 設置允許的誤差範圍
    tolerance = 5
    return all(abs(a - b) <= tolerance for a, b in zip(rgb_values, target_rgb))
"""爬蟲_應徵欄位年齡的辨識"""
def extract_age_distribution(details_div):
    # 提取年齡分佈的字典
    age_distribution = {}
    
    # 找出所有的 div 元素
    data_lines = details_div.find_elements(By.CSS_SELECTOR, 'div')
    
    for line in data_lines:
        text = line.text
        # 分割文字和百分比
        parts = text.split('\n')
        
        # 確保有兩個部分（年齡範圍和百分比）
        if len(parts) == 2:
            age_range = parts[0]
            percentage = parts[1]
            
            # 將資料加入字典
            age_distribution[age_range] = percentage
    
    return age_distribution
"""爬蟲_應徵欄位工作技能、科系、技能、證照的辨識"""
def extract_experience_distribution(details_div):
    experience_distribution = {}
    
    data_lines = details_div.find_elements(By.CSS_SELECTOR, 'div')
    
    for line in data_lines:
        text = line.text
        parts = text.split('\n')
        
        if len(parts) == 2:
            experience_range = parts[0]
            percentage = parts[1]
            
            experience_distribution[experience_range] = percentage
    
    return experience_distribution
"""儲存_上傳資料到特定資料表"""
def upload_data(data, table_name = "unknown"):
    # 插入多筆資料
    try:
        if not data:
            logging.warning("無資料可上傳")
            return
        try:
            for item in data:
                try:
                    supabase.table(table_name).insert(item).execute()
                except Exception as e:
                    logging.error(f"資料上傳失敗：{e}")
                    logging.error(f"失敗的資料：{item}")
            logging.info(f"資料上傳成功")
        except Exception as e:
            logging.error(f"資料上傳失敗：{e}")
    except Exception as e:
        logging.error(f"資料上傳到 {table_name} 表失敗：{e}")
        # 額外的診斷資訊
        logging.error(f"資料範例：{data[:1]}")
        logging.error(f"資料總筆數：{len(data)}")
"""儲存_呼叫x_save()與upload_data()每多少筆存到雲端與本地"""
def x_save(data, job_count, filename = None , sum_job = 100, 
        directory='default_directory',keyword="default_keyword", table_name = "default_table_name"):
    if job_count > 0 and job_count % sum_job ==0:
        save_to_json(data, directory=directory, filename = filename)
        if table_name == 'jobs':
            upload_data(data, table_name = table_name)
        elif table_name == 'job_tools':
            logging.warning("job_tools不上傳")
        elif table_name == 'com_url':
            logging.warning("com_url不上傳")
        elif table_name == 'job_url':
            logging.warning("job_url不上傳")
        elif table_name == 'job_skills':
            logging.warning("companies 未爬蟲")
        else:
            logging.warning("table_name 未定義")
        data.clear()
        logging.info(f"已儲存 {keyword} 職缺100筆至本地與雲端")
    return data, job_count
"""儲存_存到 json"""
def save_to_json(raw_data, filename=None, mode='w', directory='default_directory'):
    """
    將職缺資料存成 JSON 檔案
    :param job_data_list: 職缺資料列表
    :param filename: 自訂檔名，預設為當前日期時間
    :param mode: 檔案寫入模式，預設為覆蓋 'w'，可選 'a' 為附加
    :param directory: 存放位置，預設為 'default_directory'
    """
    logging.info(f"正在儲存資料至 JSON 檔案...")
    # 如果未提供檔名，使用當前日期時間
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"job_details_{timestamp}.json"
    # 確保檔名以 .json 結尾
    if not filename.endswith('.json'):
        filename += '.json'
    # 確保目錄存在
    if not os.path.exists(directory):
        os.makedirs(directory)
    # 完整的檔案路徑
    file_path = os.path.join(directory, filename)
    try:
        # 檢查檔案是否已存在且模式為附加
        if mode == 'a' and os.path.exists(file_path):
            # 讀取現有的 JSON 資料
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            # 合併新舊資料
            raw_data = existing_data + raw_data
        # 使用 UTF-8 編碼寫入 JSON 檔案
        with open(file_path, mode, encoding='utf-8') as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=4)
        logging.info(f"資料已成功儲存至 {file_path}")
        return file_path
    except Exception as e:
        logging.error(f"儲存 JSON 檔案時發生錯誤: {e}")
        return None
"""爬蟲選單_點擊並等待選項展開，根據 selector 定位元素"""
def click_and_select(selector, driver):
    """点击并等待选项展开的通用函数"""
    try:
        logging.info(f"准备点击元素: {selector}")
        element = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        logging.info(f"元素已找到，准备点击")
        driver.execute_script("arguments[0].click();", element)
        logging.info(f"元素点击完成，等待动画")
        time.sleep(1)
    except TimeoutException:
        logging.error(f"等待元素超时: {selector}")
        raise
    except Exception as e:
        logging.error(f"点击元素时发生错误: {selector}, 错误: {e}")
        raise
"""爬蟲選單_選取洲別"""
def select_continent(continent_name, driver, index):
    """选择洲别"""
    try:
        logging.info(f"开始选择洲别: {continent_name}")
        # 修改: 更新选择器以匹配实际页面结构
        # 104网站实际使用的选择器可能与之前假设的不同
        continent_element = driver.find_elements(By.XPATH, '//li[contains(@class, "category-item") and contains(@class, "category-item--level-one")]')[index]

        if continent_element:
            logging.info("找到洲别元素，准备点击")
            time.sleep(1)  # 等待滚动完成
            continent_element.click()
            logging.info(f"已完成洲别选择: {continent_name}")
            time.sleep(2)  # 增加点击后的等待时间
        else:
            raise Exception(f"无法找到洲别选项: {continent_name}")
            
    except TimeoutException as te:
        logging.error(f"等待洲别元素超时: {continent_name}")
        logging.error(f"当前页面URL: {driver.current_url}")
        logging.error(f"当前页面标题: {driver.title}")
        raise
    except Exception as e:
        logging.error(f"选择洲别时发生错误: {continent_name}, 错误: {e}")
        # 添加更多调试信息
        logging.error(f"当前页面URL: {driver.current_url}")
        logging.error(f"当前页面标题: {driver.title}")
        # 尝试获取页面源码中的部分内容
        try:
            page_source = driver.page_source
            logging.error(f"页面源码片段: {page_source[:500]}...")  # 只记录前500个字符
        except:
            logging.error("无法获取页面源码")
        raise
"""爬蟲選單_選取地區"""
def select_area(area_name, driver, area_element):
    """选择地区"""
    try:
        logging.info(f"开始选择地区: {area_name}")
        area_selector = f"button.area-item[data-area='{area_name}']"
        logging.info(f"等待地区选项出现: {area_selector}")
        logging.info(f"地区选项已找到，准备点击")
        area_element.click()
        logging.info(f"已完成地区选择: {area_name}")
        time.sleep(1)
    except Exception as e:
        logging.error(f"选择地区时发生错误: {area_name}, 错误: {e}")
        raise
"""爬蟲選單_選取區"""
def select_district(district_name, driver, district_element):
    """选择地区"""
    try:
        logging.info(f"开始选择区: {district_name}")
        district_selector = f"button.area-item[data-area='{district_name}']"
        logging.info(f"等待区选项出现: {district_selector}")
        logging.info(f"地区选项已找到，准备点击")
        district_element.click()
        logging.info(f"已完成区选择: {district_name}")
        time.sleep(1)
    except Exception as e:
        logging.error(f"选择区时发生错误: {district_name}, 错误: {e}")
        raise
"""爬蟲選單_選取產業"""
def select_industry(industry_name, driver, industries_element):
    """选择产业"""
    try:
        logging.info(f"开始选择产业: {industry_name}")
        logging.info(f"产业选项已找到，准备点击")
        industries_element.click()
        logging.info(f"已完成产业选择: {industry_name}")
        time.sleep(1)
    except Exception as e:
        logging.error(f"选择产业时发生错误: {industry_name}, 错误: {e}")
        raise
"""爬蟲選單_選取次分類"""
def select_primary_category(primary_category, driver, primary_category_element):
    """选择产业"""
    try:
        logging.info(f"开始选择产业: {primary_category}")
        logging.info(f"产业选项已找到，准备点击")
        primary_category_element.click()
        logging.info(f"已完成产业选择: {primary_category}")
        time.sleep(1)
    except Exception as e:
        logging.error(f"选择产业时发生错误: {primary_category}, 错误: {e}")
        raise
"""爬蟲選單_選取職缺"""
def select_job(job_name, driver, jobs_element):
    """选择职缺"""
    try:
        logging.info(f"开始选择职缺: {job_name}")
        logging.info(f"职缺选项已找到，准备点击")
        time.sleep(3)
        driver.execute_script("arguments[0].click();", jobs_element)
        logging.info(f"已完成职缺选择: {job_name}")
        time.sleep(1)
    except Exception as e:
        logging.error(f"选择职缺时发生错误: {job_name}, 错误: {e}")
        raise
"""爬蟲選單_確認選取後進入職缺結果頁面"""
def confirm_selection(driver):
    """确认选择并进入职缺结果页面"""
    try:
        logging.info("开始确认选择")
        logging.info("等待确认按钮出现")
        confirm_element = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.category-picker-btn-primary"))
        )
        logging.info("确认按钮已找到，准备点击")
        confirm_element.click()
        logging.info("页面加载完成")
    except TimeoutException:
        logging.error("等待确认按钮或页面加载超时")
        raise
    except Exception as e:
        logging.error(f"确认选择时发生错误: {e}")
        raise
"""抓取頁面中職缺資料，返回結果列表"""
def fetch_jobs_data(driver, max_errors=3, max_scrolls=100000, area = "", district = "", industry = "", primary_category = "", job_title = ""):
    crawler_error = 0
    logging.info(f"正在處理關鍵字: {job_title}")
    try:
        # 處理職缺
        process_jobs(driver, max_scrolls, max_errors = 3, area = area, district = district, industry = industry, primary_category = primary_category, job_title = job_title)
    except Exception as e:
        crawler_error += 1
        logging.error(f"爬蟲 {job_title} 發生錯誤: {e}")
        if crawler_error >= max_errors:
            logging.warning(f"已達到最大錯誤次數 {max_errors}")
            crawler_error = 0
'''將職缺頁滑動到最後，將所有職缺詳細頁面url存取給extract_job_info使用'''
def process_jobs(driver, max_scrolls = 100000, max_errors = 3, area = "", district = "", industry = "", primary_category = "", job_title = ""):
    scrolls = 0
    current_jobs = []
    unprocessed_jobs = []
    # 滾動並收集職缺
    while True and scrolls < max_scrolls:
        logging.info(f"正在處理第 {scrolls+1} 次滾動")
        try:
            WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, target_selector))
            )
        except TimeoutException:
            logging.warning(f"等待職缺載入超時: {WAIT_TIMEOUT} 秒")
            break
        current_jobs = driver.find_elements(By.CSS_SELECTOR, target_selector)
        unprocessed_jobs = current_jobs
        current_count = len(current_jobs)
        logging.info(f"當前頁面職缺數量: {current_count}")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        scrolls += 1
        try:
            WebDriverWait(driver, WAIT_TIMEOUT).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, target_selector)) > current_count
            )
        except TimeoutException:
            logging.info("沒有新的職缺載入，可能已到底部")
            break
    # for job in current_jobs:
    ## 測試用
    logging.info(f"共找到 {len(current_jobs)} 筆職缺")
    # 該職業所有職缺主要處理循環
    remaining_jobs = current_jobs
    while remaining_jobs:
        logging.info(f"開始處理 {len(remaining_jobs)} 個職缺")
        remaining_jobs, crawler_error = extract_job_info(remaining_jobs, driver, area = area, district = district, industry = industry, primary_category = primary_category, job_title = job_title)
        if remaining_jobs:
            logging.info(f"還有 {len(remaining_jobs)} 個職缺未處理完成")
            # 儲存未處理職缺到檔案
            try:
                with open('D:/allm/crawler/undo/unprocessed_jobs.json', 'w', encoding='utf-8') as f:
                    json.dump(remaining_jobs, f, ensure_ascii=False, indent=4)
            except Exception as e:
                logging.error(f"儲存未處理職缺時發生錯誤: {e}")
            # 重置錯誤計數器，準備下一輪處理
            crawler_error = 0
            time.sleep(5)  # 短暫暫停後繼續處理
        else:
            logging.info("所有職缺處理完成")
            break
'''將詳細頁面的資料爬取'''
def extract_job_info(current_jobs, driver, max_errors = 3, crawler_error = 0, area = "", district = "", industry = "", primary_category = "", job_title = ""):
    job_count = 0
    remaining_jobs = []
    com_list = []
    job_list = []
    for job in current_jobs:
        logging.info(f"正在處理第 {job_count+1} 筆職缺")
        if crawler_error >= max_errors:
            # 將剩餘未處理的職缺加入 remaining_jobs
            remaining_jobs=(current_jobs[job_count:])
            logging.warning(f"錯誤次數達到上限 {max_errors}，暫停處理")
            crawler_error = 0
            break
        try:
            # ※關鍵修正：從目前的職缺區塊內相對查找職缺標題與網址
            title_element = job.find_element(By.XPATH, './/h2//a[contains(@class, "info-job__text")]')
            job_url = title_element.get_attribute('href')
            job_name = title_element.get_attribute('title')
            try:
                job_industry = job.find_element(By.CSS_SELECTOR, '[data-gtm-joblist^="職缺-產業-"]').text.strip()
                logging.info(f"職缺產業{job_industry}")
            except Exception as e:
                job_industry = ""
                logging.error(f"獲取職缺產業時發生錯誤: {e}")
            # 獲取公司資訊
            company_element = job.find_element(By.CSS_SELECTOR, 'a[data-gtm-joblist="職缺-公司名稱"]')
            
            company = company_element.text.strip()
            company_url = company_element.get_attribute('href')
            # 開啟新分頁取得詳細資訊
            driver.execute_script(f"window.open('{job_url}', '_blank')")
            driver.switch_to.window(driver.window_handles[-1])
            
            WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'p.job-description__content'))
            )
            # 處理詳細頁面的資訊
            try:
                logging.info(f"職缺名稱: {job_name}")
                logging.info(f"職缺網址: {job_url}")
                # 獲取更新日期，使用 title 屬性來獲取完整日期（包含年份）
                try:
                    # update_date_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'span.text-gray-darker[title*="更新"]')))
                    update_date_element = driver.find_element(By.CSS_SELECTOR, 'span.text-gray-darker[title*="更新"]')
                    update_date = update_date_element.get_attribute('title')  # 獲取完整的 title 內容
                    update_date = update_date.replace("更新", "").strip()  # 移除 "更新" 文字
                    try:
                        # 將 update_date 轉換為 datetime 物件
                        date_obj = datetime.strptime(update_date, "%Y/%m/%d")  # 假設原始格式為 YYYY/MM/DD
                        # 格式化為 YYYY-MM-DD
                        update_date = date_obj.strftime("%Y-%m-%d")
                        logging.info(f"更新日期: {update_date}")
                    except ValueError as e:
                        # 如果日期格式不匹配，捕捉錯誤
                        logging.error(f"日期轉換失敗: {e}. 原始日期: {update_date}")
                except Exception as e:
                    update_date = "N/A"
                    logging.error(f"獲取更新日期時發生錯誤: {e}")
                    logging.info("無法獲取更新日期")
                # 檢查是否為積極徵才中（可能不存在）
                try:
                    actively_hiring = driver.find_element(By.CSS_SELECTOR, 'div.actively-hiring-tag').text.strip()
                    actively_hiring = True if actively_hiring == "積極徵才中" else False
                except:
                    actively_hiring = False
                # 獲取應徵人數
                applicants = driver.find_element(By.CSS_SELECTOR, 'a.d-flex.align-items-center.font-weight-bold').text.strip()
                # 提取數字範圍（例如："應徵人數 0~5 人" -> "0~5"）
                if applicants:
                    applicants = applicants.replace("應徵人數", "").replace("人", "").strip()
                else:
                    applicants = ""
                    logging.info(f"獲取應徵人數時發生錯誤: {e}")
                try:
                    # 獲取工作內容
                    job_description = driver.find_element(By.CSS_SELECTOR, 'p.job-description__content').text.strip()
                except Exception as e:
                    job_description = ""
                    logging.error(f"獲取工作內容時發生錯誤: {e}")
                try:
                    # 獲取職務類別
                    job_categories = driver.find_elements(By.CSS_SELECTOR, 'div.category-item u')
                    job_category = '、'.join([cat.text for cat in job_categories])
                except Exception as e:
                    job_category = ""
                    logging.error(f"獲取職務類別時發生錯誤: {e}")
                try:
                    # 獲取工作待遇
                    salary = driver.find_element(By.CSS_SELECTOR, 'p.text-primary.font-weight-bold').text.strip()
                except Exception as e:
                    salary = ""
                    logging.error(f"獲取工作待遇時發生錯誤: {e}")
                try:
                    # 獲取工作性質
                    job_type = driver.find_element(By.CSS_SELECTOR, 'div.list-row:nth-child(4) div.list-row__data').text.strip()
                except Exception as e:
                    job_type = ""
                    logging.error(f"獲取工作性質時發生錯誤: {e}")
                try:
                    # 獲取上班地點
                    location = driver.find_element(By.CSS_SELECTOR, 'div.job-address span').text.strip()
                except Exception as e:
                    location = ""
                    logging.error(f"獲取上班地點時發生錯誤: {e}")
                try:
                    # 獲取管理責任
                    management_elements = driver.find_elements(By.CSS_SELECTOR, 'div.list-row')
                    management = ""
                    for element in management_elements:
                        try:
                            title_text = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title_text == "管理責任":
                                management = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                                break
                        except Exception as e:
                            logging.error(f"獲取管理責任時發生錯誤: {e}")
                            continue
                except Exception as e:
                    management = ""
                    logging.error(f"獲取管理責任時發生錯誤: {e}")
                try:
                    # 獲取出差外派
                    business_trip = ""
                    for element in management_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "出差外派":
                                business_trip = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                                break
                        except Exception as e:
                            logging.error(f"獲取出差外派時發生錯誤: {e}")
                            continue
                    # 獲取上班時段
                    work_time = ""
                    for element in management_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "上班時段":
                                work_time = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                                break
                        except Exception as e:
                            logging.error(f"獲取上班時段時發生錯誤: {e}")
                            continue
                    # 獲取休假制度
                    vacation = ""
                    for element in management_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "休假制度":
                                vacation = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                                break
                        except Exception as e:
                            logging.error(f"獲取休假制度時發生錯誤: {e}")
                            continue
                    # 獲取可上班日
                    start_work = ""
                    for element in management_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "可上班日":
                                start_work = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                                break
                        except Exception as e:
                            logging.error(f"獲取可上班日時發生錯誤: {e}")
                            continue
                    # 獲取需求人數
                    headcount = ""
                    for element in management_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "需求人數":
                                headcount = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                                break
                        except Exception as e:
                            logging.error(f"獲取需求人數時發生錯誤: {e}")
                            continue
                except Exception as e:
                    business_trip = ""
                    work_time = ""
                    vacation = ""
                    start_work = ""
                    headcount = ""
                    logging.error(f"獲取工作條件時發生錯誤: {e}")
                # 獲取工作經歷
                work_exp = ""
                work_exp_elements = driver.find_elements(By.CSS_SELECTOR, 'div.list-row')
                try:
                    for element in work_exp_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "工作經歷":
                                work_exp = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                                break
                        except Exception as e:
                            logging.error(f"獲取工作經歷時發生錯誤: {e}")
                            continue
                    # 獲取學歷要求
                    education = ""
                    for element in work_exp_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "學歷要求":
                                education = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                                break
                        except Exception as e:
                            logging.error(f"獲取學歷要求時發生錯誤: {e}")
                            continue
                    # 獲取科系要求
                    major = ""
                    for element in work_exp_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "科系要求":
                                major = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                                break
                        except Exception as e:
                            logging.error(f"獲取科系要求時發生錯誤: {e}")
                            continue
                    # 獲取語文條件
                    language = ""
                    for element in work_exp_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "語文條件":
                                language = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                                break
                        except Exception as e:
                            logging.error(f"獲取語文條件時發生錯誤: {e}")
                            continue
                    # 獲取擅長工具
                    tools = ""
                    for element in work_exp_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "擅長工具":
                                tools_elements = element.find_elements(By.CSS_SELECTOR, 'div.list-row__data u')
                                tools = '、'.join([tool.text for tool in tools_elements])
                                break
                        except Exception as e:
                            logging.error(f"獲取擅長工具時發生錯誤: {e}")
                            continue
                    # 獲取工作技能
                    skills = ""
                    for element in work_exp_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "工作技能":
                                skills_elements = element.find_elements(By.CSS_SELECTOR, 'div.list-row__data u')
                                skills = '、'.join([skill.text for skill in skills_elements])
                                break
                        except Exception as e:
                            logging.error(f"獲取工作技能時發生錯誤: {e}")
                            continue
                    # 獲取具備證照
                    certificates = ""
                    for element in work_exp_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "具備證照":
                                cert_elements = element.find_elements(By.CSS_SELECTOR, 'div.list-row__data u')
                                certificates = '、'.join([cert.text for cert in cert_elements])
                                break
                        except Exception as e:
                            logging.error(f"獲取具備證照時發生錯誤: {e}")
                            continue
                    # 獲取其他條件
                    other_requirements = ""
                    for element in work_exp_elements:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title == "其他條件":
                                other_requirements = element.find_element(By.CSS_SELECTOR, 'div.list-row__data p.r3').text.strip()
                                break
                        except Exception as e:
                            logging.info("其他條件無資訊")
                            continue
                except Exception as e:
                    work_exp = ""
                    education = ""
                    major = ""
                    language = ""
                    tools = ""
                    skills = ""
                    certificates = ""
                    other_requirements = ""
                    logging.error(f"獲取工作條件時發生錯誤: {e}")
                # 獲取福利制度
                # 法定項目
                legal_benefits = []
                legal_elements = driver.find_elements(By.CSS_SELECTOR, 'div.benefits-labels:nth-child(3) span.tag--text a')
                if legal_elements: 
                    legal_benefits = [item.text.strip() for item in legal_elements]
                    legal_benefits_str = '、'.join(legal_benefits)
                else:
                    logging.info("法定項目無資訊")
                    legal_benefits_str = ""
                # 其他福利
                other_benefits = []
                other_elements = driver.find_elements(By.CSS_SELECTOR, 'div.benefits-labels:nth-child(5) span.tag--text a')
                if other_elements:
                    other_benefits = [item.text.strip() for item in other_elements]
                    other_benefits_str = '、'.join(other_benefits)
                else:
                    logging.info("其他福利無資訊")
                    other_benefits_str = ""
                # 未整理的福利說明
                raw_benefits = ""
                benefits_description = driver.find_element(By.CSS_SELECTOR, 'div.benefits-description p.r3')
                if benefits_description:
                    raw_benefits = benefits_description.text.strip()     
                else:
                    logging.info("未整理的福利說明無資訊")
                    raw_benefits = ""
                # 獲取聯絡方式
                contact_info = []
                contact_elements = driver.find_elements(By.CSS_SELECTOR, 'div.job-contact-table div.job-contact-table__data')
                if contact_elements:
                    contact_info = [element.text.strip() for element in contact_elements]
                    contact_info_str = '\n'.join(contact_info)
                else:
                    logging.info("聯絡方式無資訊")
                    contact_info_str = ""     
                try:
                    logging.info("開始開啟應徵分頁")
                    # 開啟應徵分頁獲取詳細資訊
                    # 從原始工作頁面 URL 提取工作代碼
                    apply_code = job_url.split('/')[-1].split('?')[0]
                    # 構建應徵分析頁面的 URL
                    try:
                        apply_analysis_url = f"https://www.104.com.tw/jobs/apply/analysis/{apply_code}"
                        driver.execute_script(f"window.open('{apply_analysis_url}', '_blank')")
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(5)
                    except Exception as e:
                        logging.error(f"分析與開啟應徵分析頁面代碼發生錯誤: {e}")
                    # 抓取教育程度分布
                    apply_education = {}
                    education_elements = driver.find_elements(By.CSS_SELECTOR, "div.legend__text")
                    education_values = driver.find_elements(By.CSS_SELECTOR, "div.legend__value") 
                    try:
                        for i in range(len(education_elements)):
                            apply_education[education_elements[i].text] = education_values[i].text
                    except Exception as e:
                        apply_education = {}
                        logging.info("教育程度分佈無資料")
                    # 抓取性別分布
                    gender = {"男性":"", "女性":""}
                    gender_elements = driver.find_elements(By.CSS_SELECTOR, ".stack-bar__text__block")
                    if gender_elements:
                        for element in gender_elements[:2]:
                            style = element.get_attribute("style")
                            if "rgb" in style:
                                rgb_value = style[style.find("rgb"):style.find(")") + 1]
                                rgb_value = rgb_value.strip()
                                rgb_value = rgb_value.replace("rgb(", "").replace(")", "")
                                rgb_value = [int(x) for x in rgb_value.split(",")]
                                gender_text = element.find_element(By.CSS_SELECTOR, "div").text
                                male_rgb = [78, 145, 255]    # 藍色
                                female_rgb = [255, 144, 199]  # 粉色
                                if is_similar_rgb(rgb_value, male_rgb):
                                    gender["男性"] = gender_text
                                elif is_similar_rgb(rgb_value, female_rgb):
                                    gender["女性"] = gender_text
                    else:
                        gender = {}
                        logging.info("性別分佈無資料")
                    # 抓取語言能力
                    # 選取div.chart-container__body的第5個是下下之策
                    # language_container = driver.find_elements(By.CSS_SELECTOR, "div.chart-container__body")[5]
                    logging.info("開始抓取語言能力")
                    language_containers = driver.find_elements(By.CSS_SELECTOR, "div.chart-container__body")
                    if len(language_containers) > 5:
                        language_container = language_containers[5]
                        # 初始化語言能力字典
                        language_skills = {}
                        # 找出所有語言項目
                        language_items = language_container.find_elements(By.XPATH, ".//div[contains(@class, 'mb-4')]")
                        for language_item in language_items:
                            # 提取語言名稱
                            language_name = language_item.find_element(By.XPATH, ".//span[contains(@class, 'text-truncate')]").text
                            # 找出該語言的技能等級和百分比
                            skill_bars = language_item.find_elements(By.XPATH, ".//div[contains(@class, 'stack-bar__text__block')]")
                            # 建立該語言的技能描述
                            language_description = []
                            # 圖例映射
                            legend_map = {
                                "rgb(255, 231, 217)": "不會",
                                "rgb(255, 213, 189)": "略懂",
                                "rgb(255, 195, 161)": "中等",
                                "rgb(204, 156, 129)": "精通"
                            }
                            for bar in skill_bars:
                                try:
                                    percentage = bar.text
                                    # 獲取背景顏色
                                    background_color = bar.get_attribute('style').split('background:')[1].split(';')[0].strip()
                                    skill_level = legend_map.get(background_color, "未知")
                                    language_description.append(f"{skill_level}{percentage}")
                                except Exception as e:
                                    logging.info("語言技能分佈無資料")
                            # 將語言技能加入字典
                            language_skills[language_name] = ','.join(language_description)                        
                    else:
                        logging.error("語言能力容器數量不足")
                    # 定位所有的圖表容器
                    chart_containers = driver.find_elements(By.CSS_SELECTOR, 'div.chart-container.d-flex.flex-column.bg-white.overflow-hidden.horizontal-bar-chart')
                    if chart_containers:
                        # 欄位名稱列表
                        fields = {
                            '年齡': extract_age_distribution,
                            '工作經驗': extract_experience_distribution,
                            '科系': extract_experience_distribution,  # 可以重複使用
                            '技能': extract_experience_distribution,
                            '證照': extract_experience_distribution
                        }
                        # 遍歷每個圖表容器
                        for container in chart_containers:
                            # 找出標題 DIV
                            title_div = container.find_element(By.CSS_SELECTOR, 'div:first-child')
                            # 找出詳細資訊 DIV
                            details_div = container.find_element(By.CSS_SELECTOR, 'div:last-child')
                            # 獲取標題
                            title = title_div.text
                            # 根據標題提取資料
                            if title in fields:
                                # 使用對應的提取方法
                                extraction_method = fields[title]
                                extracted_data = extraction_method(details_div)
                                # 根據標題存儲到對應的變數
                                if title == '年齡':
                                    try:
                                        age_distribution = extracted_data
                                    except Exception as e:
                                        logging.info("年齡分佈無資料")
                                        age_distribution = {}
                                elif title == '工作經驗':
                                    try:
                                        work_experience = extracted_data
                                    except Exception as e:
                                        logging.info("工作經驗分佈無資料")
                                        work_experience = {}
                                elif title == '科系':
                                    try:
                                        major_distribution = extracted_data
                                    except Exception as e:
                                        logging.info("科系分佈無資料")
                                        major_distribution = {}
                                elif title == '技能':
                                    try:
                                        skills_distribution = extracted_data
                                    except Exception as e:
                                        logging.info("技能分佈無資料")
                                        skills_distribution = {}
                                elif title == '證照':
                                    try:
                                        certificates_distribution = extracted_data
                                    except Exception as e:
                                        logging.info("證照分佈無資料")
                                        certificates_distribution = {}
                                else:
                                    logging.info(f"未知的標題: {title}")
                            else:
                                logging.info(f"未知的標題: {title}")
                    else:
                        logging.error("應徵眾多資訊無資訊")
                    # 關閉應徵頁面，切回列表頁
                    driver.close()
                    driver.switch_to.window(driver.window_handles[-1])
                except Exception as e:
                    # 關閉應徵頁面，切回列表頁
                    driver.close()
                    driver.switch_to.window(driver.window_handles[-1])
                    logging.error(f"獲取應徵詳細資訊時發生錯誤: {e}")
                    apply_education, gender, language_skills, age_distribution, work_experience, major_distribution, skills_distribution, certificates_distribution = {}
                "apply_education"=={} 
                "apply_gender"== {}
                "apply_language"== {}
                "apply_age_distribution"== {}
                "apply_experience"== {}
                "apply_major"== {}
                "apply_skills"== {}
                "apply_certificates"== {}                      
                time.sleep(3)
                # 更新要存入的資料
                logging.info(f"更新要存入的資料")
                try:
                    parts = company_url.split('/')
                    if len(parts) >= 5:
                        # 以下假設 URL 格式為 "https://www.104.com.tw/company/ID?..."
                        company_id = parts[4].split('?')[0]
                        com_list.append({"company_url":company_url, "company_id":company_id})  
                    else:
                        com_list.append({"company_url":"", "company_id":""})
                        raise ValueError("URL 格式錯誤: " + company_url)
                except Exception as e:
                    logging.error(f"處理公司網址時發生錯誤: {e}")
                try:
                    job_list.append({
                        "job_id":apply_code+update_date,
                        "job_name":job_name, "job_industry":job_industry, "area":area+district, "industry": industry, "primary_category":primary_category, 
                        "job_title":job_title,"company_name":company, "update_date":update_date, "actively_hiring":actively_hiring, 
                        "applicants":applicants, "job_description":job_description, "job_category":job_category, "salary":salary, "job_type":job_type, 
                        "location":location, "management":management, "business_trip":business_trip, "work_time":work_time, "vacation":vacation, 
                        "start_work":start_work, "headcount":headcount, "work_exp":work_exp, "education":education, "major":major, 
                        "language":language, "skills":skills, "tools": tools, "certificates":certificates, "other_requirements":other_requirements,
                        "legal_benefits":legal_benefits_str, "other_benefits":other_benefits_str, "raw_benefits":raw_benefits, "contact_info":contact_info_str,
                        "apply_education":apply_education, "apply_gender": gender, "apply_language": language_skills, "apply_age_distribution": age_distribution,
                        "apply_experience": work_experience, "apply_major": major_distribution, "apply_skills": skills_distribution, "apply_certificates": certificates_distribution,
                        "status": "active"                     
                    })
                except Exception as e:
                    logging.error(f"處理職缺時發生錯誤: {e}")

                job_count+=1
            except Exception as e:
                logging.error(f"處理詳細頁面資訊時發生錯誤: {e}")
                job_list.append({
                    "job_id":apply_code+update_date,
                    "job_name":job_name, "job_industry":job_industry, "area":area+district, "industry": industry, "primary_category":primary_category, 
                    "job_title":job_title,"company_name":company, "update_date":update_date, "actively_hiring":actively_hiring, 
                    "applicants":"", "job_description": "", "job_category": "", "salary": "", "job_type": "",
                    "location": "", "management": "", "business_trip": "", "work_time": "",
                    "vacation": "", "start_work": "", "headcount": "", "work_exp": "", "education": "", 
                    "major":"", "language":"", "skills":"", "tools":"", "certificates":"", 
                    "other_requirements":"", "legal_benefits":"", "other_benefits":"", "raw_benefits":"", "contact_info":"", "status": "draft",
                    "apply_education":{}, "apply_gender": {}, "apply_language": {}, "apply_age_distribution": {},
                    "apply_experience": {}, "apply_major": {}, "apply_skills": {}, "apply_certificates": {}
                    # 新增欄位的空值
                })             
                com_list.append({"company_url":"", "company_id":""})
                job_count +=1
                # if sum(1 for field in job_list[-1] if field == "") > 6:
                #     crawler_error += 1
                #     logging.info("職缺超過六個空缺")
            # 關閉詳細頁面，切回列表頁
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            # 儲存資料
            try:
                job_list_count = len(job_list)
                logging.info(f"目前第{job_list_count}個職缺，儲存資料")
                x_save(job_list, job_count= job_list_count,directory='D:/allm/crawler/job_list',keyword = "job_list", table_name='jobs')
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"com_url_{timestamp}.json"
                x_save(com_list, job_count= job_list_count,filename = filename ,directory='D:/allm/crawler/com_url', keyword="com_url", table_name="com_url")
            except Exception as e:
                logging.error(f"儲存時發生錯誤: {e}")
        except Exception as e:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            logging.error(f"處理職缺時發生錯誤: {e}")
            crawler_error += 1
    if len(job_list)>0:
        # job_list_count = len(job_list)
        # logging.info(f"目前第{job_list_count}個職缺，儲存資料")
        # x_save(job_list, job_count= job_list_count,directory='D:/allm/crawler/job_list',keyword = "job_list", table_name='jobs')
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # filename = f"com_url_{timestamp}.json"
        # x_save(com_list, job_count= job_list_count,filename = filename ,directory='D:/allm/crawler/com_url', keyword="com_url", table_name="com_url")
        # def upload_data(data, table_name = "unknown"):
        # def save_to_json(raw_data, filename=None, mode='w', directory='default_directory'):
        save_to_json(job_list, directory='D:/allm/crawler/job_list')
        upload_data(job_list, table_name='jobs')
        job_list = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"com_url_{timestamp}.json"
        save_to_json(com_list,filename = filename , directory='D:/allm/crawler/com_url')
        com_list = []
    return remaining_jobs, crawler_error
def crawl():
    logging.info("开始爬取程序")
    driver = setup_driver()
    logging.info("浏览器驱动初始化完成")
    base_url = "https://www.104.com.tw/jobs/search"
    logging.info(f"准备访问网站: {base_url}")
    driver.get(base_url)
    logging.info("网站加载完成")
    # 等待并点击地区按钮
    logging.info("等待地区按钮出现...")
    area_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-gtm-joblist='搜尋欄位-地區']")))
    area_button.click()
    # 洲别选取
    logging.info("开始处理洲别选择")
    try:
        continents_to_iterate = target_continent if target_continent else []
    except Exception as e:
        logging.error(f"處理洲別時發生錯誤1: {e}")
    try:
        time.sleep(3)
        continent_elements = driver.find_elements(By.XPATH, '//li[contains(@class, "category-item") and contains(@class, "category-item--level-one")]')
        # category-item category-item--focus category-item--level-one
    except Exception as e:
        logging.error(f"處理洲別時發生錯誤2: {e}")
    try:
        continent_texts = [element.text for element in continent_elements]
    except Exception as e:
        logging.error(f"處理洲別時發生錯誤3: {e}")   
    logging.info(continent_texts)
    if not continents_to_iterate:
        logging.info("未指定目标洲别，将选取所有洲别")
        continent_elements = driver.find_elements(By.XPATH, '//li[contains(@class, "category-item") and contains(@class, "category-item--level-one")]')
        continents_to_iterate = [elem.text for elem in continent_elements]
        logging.info(f"找到以下洲别: {continents_to_iterate}")
    con_select_count = 0
    for continent in continents_to_iterate:
        logging.info(f"=== 开始处理洲别: {continent} ===")
        continent_index = continent_texts.index(continent)
        if con_select_count != 0:
            area_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-gtm-joblist='搜尋欄位-地區']")))
            area_button.click()            
        select_continent(continent, driver, continent_index)
        # 地区选取
        logging.info("开始处理縣市选择")
        area_elements = driver.find_elements(By.XPATH, f'//li[contains(@class, "category-item") and contains(@class, "category-item--level-two")]')
        area_texts = [a.text for a in area_elements if a.text not in nouse_area]
        logging.info(f"找到以下可用縣市: {area_texts}")
        area_select_count = 0
        for area in area_texts:
            logging.info(f"=== 开始处理縣市: {area} ===")
            area_index = area_texts.index(area)
            area_element = area_elements[area_index]
            if area_select_count != 0:
                area_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-gtm-joblist='搜尋欄位-地區']")))
                area_button.click()
                select_continent(continent, driver, continent_index)                
            select_area(area, driver, area_element)
            # 區 選取
            logging.info("开始处理行政區選擇")
            district_elements = driver.find_elements(By.XPATH, f'//li[contains(@class, "category-item") and contains(@class, "category-item--level-three")]')
            district_texts = [a.text for a in district_elements if a.text != "" and a.text not in nouse_district]
            logging.info(f"找到以下可用行政區: {district_texts}")
            dis_select_count = 0
            for district in district_texts:
                logging.info(f"=== 开始处理行政區: {district} ===")
                district_index = district_texts.index(district)
                district_element = district_elements[district_index]
                if dis_select_count != 0:
                    area_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-gtm-joblist='搜尋欄位-地區']")))
                    area_button.click()
                    select_continent(continent, driver, continent_index)
                    select_area(area, driver, area_element)                    
                select_district(district, driver, district_element)
                confirm_selection(driver)
                # 产业选取
                logging.info("开始处理产业选择")
                try:
                    industries_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-gtm-joblist='搜尋欄位-職類']")))
                    industries_button.click()
                except Exception as e:
                    logging.error(f"產業案件錯誤{e}")
                time.sleep(3)
                industries_to_iterate = target_industry if target_industry else []
                # 所有產業的網頁元素
                industries_elements = driver.find_elements(By.XPATH, '//li[contains(@class, "category-item") and contains(@class, "category-item--level-one")]')
                # 所有產業的文字
                industries_texts = [element.text for element in industries_elements]
                logging.info(industries_texts)
                if not industries_to_iterate:
                    logging.info("未指定目标产业，将选取全部产业")
                    industries_to_iterate = industries_texts
                    logging.info(f"选择的产业: {industries_to_iterate}")
                ind_select_count = 0
                for industry in industries_to_iterate:
                    logging.info(f"=== 开始处理产业: {industry} ===")
                    indus_index = industries_texts.index(industry)
                    industries_element = industries_elements[indus_index]
                    if ind_select_count != 0:
                        try:
                            industries_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-gtm-joblist='搜尋欄位-職類']")))
                            industries_button.click()
                        except Exception as e:
                            logging.error(f"產業按鍵錯誤: {e}")
                    select_industry(industry, driver, industries_element)
                    # 次要職業分類选取
                    primary_category_to_iterate = target_primary_category if target_primary_category else []
                    primary_category_elements = driver.find_elements(By.XPATH, '//li[contains(@class, "category-item") and contains(@class, "category-item--level-two")]')
                    primary_category_texts = [a.text for a in primary_category_elements if a.text not in nouxe_primary_category]
                    logging.info(f"找到以下可用次分類: {primary_category_texts}")
                    logging.info("开始处理次要职缺选择")
                    if not primary_category_to_iterate:
                        logging.info("未指定目标次分類，将选取全部次分類")
                        primary_category_to_iterate = primary_category_texts
                        logging.info(f"选择的次分類:{primary_category_to_iterate}")
                    pc_select_count = 0
                    for primary_category in primary_category_to_iterate:
                        logging.info(f"=== 开始处理次分類: {primary_category} ===")
                        prim_index = primary_category_texts.index(primary_category)
                        primary_category_element = primary_category_elements[prim_index]
                        if pc_select_count ==0:
                            select_primary_category(primary_category, driver, primary_category_element)
                        else:
                            try:
                                industries_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-gtm-joblist='搜尋欄位-職類']")))
                                industries_button.click()
                            except Exception as e:
                                logging.error(f"產業按鍵錯誤{e}")                            
                            select_primary_category(primary_category, driver, primary_category_element)
                        # 職業選取
                        jobs_to_iterate = target_jobs if target_jobs else []
                        jobs_elements = driver.find_elements(By.XPATH, '//li[contains(@class, "category-item") and contains(@class, "category-item--level-three")]')
                        jobs_texts = [a.text for a in jobs_elements if a not in nouxe_jobs]
                        logging.info("开始处理職務选择")
                        if not jobs_to_iterate:
                            logging.info("未指定目标職務，将选取全部職業")
                            jobs_to_iterate = jobs_texts
                        jobs_count=0
                        logging.info(f"选择的職務: {jobs_to_iterate}")
                        jobs_to_iterate = [item for item in jobs_to_iterate if item != '']
                        logging.info(f"选择的職務: {jobs_to_iterate}")
                        for job_title in jobs_to_iterate:
                            logging.info(f"=== 开始处理職務: {job_title} ===")
                            job_index = jobs_texts.index(job_title)
                            ex_job_index = jobs_texts.index(job_title) -1
                            jobs_element = jobs_elements[job_index]
                            ex_jobs_element = jobs_elements[ex_job_index]
                            if jobs_count ==0:
                                select_job(job_title, driver, jobs_element)
                                confirm_selection(driver)
                                confirm_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-gtm-joblist='搜尋欄位-搜尋點擊']")))
                                logging.info("确认按钮已找到，准备点击")
                                confirm_element.click()
                                logging.info("开始获取职缺数据")
                                fetch_jobs_data(driver, max_errors=3, max_scrolls=10000, area = area, district = district, industry = industry, primary_category = primary_category, job_title = job_title)
                                logging.info(f"完成职缺 {job_title} 的数据获取")                               
                            else:
                                try:
                                    industries_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-gtm-joblist='搜尋欄位-職類']")))
                                    industries_button.click()
                                except Exception as e:
                                    logging.error(f"產業案件錯誤{e}")
                                select_job(job_title, driver, jobs_element)
                                confirm_selection(driver)
                                confirm_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-gtm-joblist='搜尋欄位-搜尋點擊']")))
                                logging.info("确认按钮已找到，准备点击")
                                confirm_element.click()
                                logging.info("开始获取职缺数据")
                                fetch_jobs_data(driver, max_errors=3, max_scrolls=10000, area = area, district = district, industry = industry, primary_category = primary_category, job_title = job_title)
                                logging.info(f"完成职缺 {job_title} 的数据获取")                                                      
                            try:
                                industries_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-gtm-joblist='搜尋欄位-職類']")))
                                industries_button.click()
                            except Exception as e:
                                logging.error(f"產業按鍵錯誤{e}")
                            select_job(job_title, driver, jobs_element)
                            confirm_selection(driver)                            
                            jobs_count +=1
                        pc_select_count += 1
                industries_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-gtm-joblist='搜尋欄位-職類']")))
                industries_button.click()                
                dis_select_count += 1
                select_district(district, driver, district_element)
                confirm_selection(driver)
            area_select_count += 1           
        con_select_count +=1
    logging.info("所有数据爬取完成")
    driver.quit()
    logging.info("浏览器已关闭，程序结束")
if __name__ == "__main__":
    log_file = setup_logging()
    logging.info(f"日誌檔案已建立：{log_file}")
    # 建立 Supabase 客戶端
    supabase: Client = create_client(supabase_url, supabase_key)
    # 建立 為執行職缺暫存資料夾
    os.makedirs('D:/allm/crawler/undo', exist_ok=True)
    crawl()
    if len(job_list) > 0:
        x_save(job_list, job_count= 2,directory='D:/allm/crawler/job_list', table_name='jobs')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        x_save(com_list, job_count= 2,filename = f"com_url_{timestamp}.json" ,directory='D:/allm/crawler/com_url', table_name="com_url")
    logging.info("職缺爬蟲程式執行完畢")


