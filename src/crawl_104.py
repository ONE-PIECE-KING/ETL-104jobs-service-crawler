'''
# %pip install selenium-wire==5.1.0
# %pip install blinker==1.5
import tempfile
import requests
import random
import re
'''
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
import pandas as pd
import logging
from supabase import create_client, Client
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
# 在程式開始前呼叫 setup_logging()
log_file = setup_logging()
logging.info(f"日誌檔案已建立：{log_file}")
# 設定 Selenium 選項
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

chrome_options.add_argument('--start-maximized')
# port號 一個爬蟲程序只能一個
chrome_options.add_argument('--remote-debugging-port=9222')
chrome_options.add_argument('--disable-gpu')

# 隨機 User Agent
ua = UserAgent()
chrome_options.add_argument(f'user-agent={ua.random}')
# 根據環境設定 Chrome 路徑
if os.path.exists("/usr/bin/chromium"):  # Docker 環境
    chrome_options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
else:  # Windows 本地環境
    service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
# 執行 CDP 命令以隱藏 WebDriver 屬性
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
    Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
    })
    """
})
driver.command_executor.set_timeout(1000)
# 設定 Supabase 連線參數
supabase_url: str = "url"
supabase_key: str = "key"
# 建立 Supabase 客戶端
supabase: Client = create_client(supabase_url, supabase_key)
# 檢查 Chrome 和 ChromeDriver 的版本
def check_chrome_driver_version():
    # 獲取 Chrome 瀏覽器版本
    chrome_version = subprocess.check_output(
        ['google-chrome', '--version']
    ).decode('utf-8').strip().split(' ')[-1]
    
    # 獲取 ChromeDriver 版本
    driver_version = subprocess.check_output(
        ['chromedriver', '--version']
    ).decode('utf-8').strip().split(' ')[-1]

    if chrome_version != driver_version:
        logging.warning(f"版本不匹配！Chrome: {chrome_version}, ChromeDriver: {driver_version}")
        # 自動下載與 Chrome 版本相符的 ChromeDriver
        logging.info("正在下載正確版本的 ChromeDriver...")
        driver_path = ChromeDriverManager().install()
        return driver_path
    else:
        return None

# 應徵欄位的辨識
def is_similar_rgb(rgb_str, target_rgb):
    # 從rgb字符串中提取數值
    rgb_values = [int(x) for x in rgb_str.replace("rgb(", "").replace(")", "").split(",")]
    # 允許的誤差範圍
    tolerance = 5
    
    return all(abs(a - b) <= tolerance for a, b in zip(rgb_values, target_rgb))
# 應徵欄位的辨識
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
# 應徵欄位的辨識
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

# 上傳資料到特定資料表
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
def x_save(data, job_count, filename = None , sum_job = 100, 
        directory='default_directory', keyword = 'default_keyword_list', table_name = "default_table_name"):
    if job_count > 0 and job_count % sum_job ==0:
        save_to_json(data, directory=directory, filename = filename)
        if table_name == 'jobs':
            upload_data(data, table_name = table_name)
        elif table_name == 'job_tools':
            upload_data(data, table_name = table_name)
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
# 存到 json
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
# line api
'''
# def line_request(msg = 'hi'):
#     # 注意前方要有 Bearer
#     headers = {'Authorization':'Bearer R8QHtMLcDnyilFU=','Content-Type':'application/json'}
#     body = {
#         'to':'U53129a6be4ca475a77ef6',
#         'messages':[{
#                 'type': 'text',
#                 'text': msg
#             }]
#         }
#     # 向指定網址發送 request
#     req = requests.request('POST', 'https://api.line.me/v2/bot/message/push',headers=headers,data=json.dumps(body).encode('utf-8'))
#     # 印出得到的結果
#     logging.info(req.text)
'''
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
def crawl_jobs(keyword_list, max_errors=3, max_scrolls=100000):
    crawler_error = 0
    for keyword in keyword_list:
        logging.info(f"正在處理關鍵字: {keyword}")
        try:
            # 爬蟲邏輯
            url = f"https://www.104.com.tw/jobs/search/?keyword={keyword}"
            driver.get(url)
            time.sleep(5)
            # 處理職缺
            process_jobs(driver, max_scrolls, max_errors = 3,keyword=keyword)
        except Exception as e:
            crawler_error += 1
            logging.error(f"爬蟲 {keyword} 發生錯誤: {e}")
            if crawler_error >= max_errors:
                logging.warning(f"已達到最大錯誤次數 {max_errors}，停止爬蟲")
                break
def process_jobs(driver, max_scrolls = 100000, max_errors = 3, keyword = 'default_keyword'):
    scrolls = 0
    current_jobs = []
    # 用來記錄尚未處理完的職缺（例如記錄其標題與 URL）
    unprocessed_jobs = []
    while True and scrolls < max_scrolls:
        logging.info(f"正在處理第 {scrolls+1} 次滾動")
        '''
        try:
            current_jobs = driver.find_elements(By.CSS_SELECTOR, target_selector)
            logging.info(f"目前職缺數量: {len(current_jobs)}")
            if len(current_jobs) == 0:
                logging.warning("沒有找到職缺元素")
                break
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            logging.info(f"已經滾動 {scrolls+1} 次，目前職缺數量: {len(current_jobs)}")
            time.sleep(2)
            
            current_jobs = driver.find_elements(By.CSS_SELECTOR, target_selector)
            if len(current_jobs) == previous_jobs_count:  # 元素數量沒有變化
                break
            previous_jobs_count = len(current_jobs)
            scrolls += 1
        except Exception as e:
            logging.error(f"滾動到下一頁時發生錯誤: {e}")
            break
        '''
        try:
            WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, target_selector))
            )
        except TimeoutException:
            logging.warning(f"等待職缺載入超時: {WAIT_TIMEOUT} 秒")
            break
        current_jobs = driver.find_elements(By.CSS_SELECTOR, target_selector)
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
    def extract_job_info(current_jobs, max_errors = 3, crawler_error = 0):
        job_count=0
        for job in current_jobs:
        # 測試用
        # for job in current_jobs[:4]:
            if  crawler_error < max_errors:
                logging.info(f"正在處理第 {job_count+1} 筆職缺")
                try:
                    # ※關鍵修正：從目前的職缺區塊內相對查找職缺標題與網址
                    title_element = job.find_element(By.XPATH, './/h2//a[contains(@class, "info-job__text")]')
                    job_url = title_element.get_attribute('href')
                    job_name = title_element.get_attribute('title')
                    
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
                        # logging.info(f"公司名稱: {company}")
                        # 獲取更新日期，使用 title 屬性來獲取完整日期（包含年份）
                        try:
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
                        try:
                            applicants = driver.find_element(By.CSS_SELECTOR, 'a.d-flex.align-items-center.font-weight-bold').text.strip()
                            # 提取數字範圍（例如："應徵人數 0~5 人" -> "0~5"）
                            applicants = applicants.replace("應徵人數", "").replace("人", "").strip()
                        except Exception as e:
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
                                    logging.info(f"獲取其他條件時發生錯誤: {e}")
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
                        try:
                            # 法定項目
                            legal_benefits = []
                            legal_elements = driver.find_elements(By.CSS_SELECTOR, 'div.benefits-labels:nth-child(3) span.tag--text a')
                            legal_benefits = [item.text.strip() for item in legal_elements]
                            legal_benefits_str = '、'.join(legal_benefits)
                            # 其他福利
                            other_benefits = []
                            other_elements = driver.find_elements(By.CSS_SELECTOR, 'div.benefits-labels:nth-child(5) span.tag--text a')
                            other_benefits = [item.text.strip() for item in other_elements]
                            other_benefits_str = '、'.join(other_benefits)
                            # 未整理的福利說明
                            raw_benefits = ""
                            benefits_description = driver.find_element(By.CSS_SELECTOR, 'div.benefits-description p.r3').text.strip()
                            raw_benefits = benefits_description             
                        except Exception as e:
                            logging.info(f"獲取福利制度時發生錯誤: {e}")
                            legal_benefits_str = ""
                            other_benefits_str = ""
                            raw_benefits = ""
                        
                        # 獲取聯絡方式
                        try:
                            contact_info = []
                            contact_elements = driver.find_elements(By.CSS_SELECTOR, 'div.job-contact-table div.job-contact-table__data')
                            contact_info = [element.text.strip() for element in contact_elements]
                            contact_info_str = '\n'.join(contact_info)
                        except Exception as e:
                            logging.info(f"獲取聯絡方式時發生錯誤: {e}")
                            contact_info_str = ""     
                        try:
                            # 開啟應徵分頁獲取詳細資訊
                            # 從原始工作頁面 URL 提取工作代碼
                            apply_code = job_url.split('/')[-1].split('?')[0]
                            # 構建應徵分析頁面的 URL
                            apply_analysis_url = f"https://www.104.com.tw/jobs/apply/analysis/{apply_code}"
                            driver.execute_script(f"window.open('{apply_analysis_url}', '_blank')")
                            driver.switch_to.window(driver.window_handles[-1])
                            time.sleep(5)
                            # 抓取教育程度分布
                            try:
                                apply_education = {}
                                education_elements = driver.find_elements(By.CSS_SELECTOR, "div.legend__text")
                                education_values = driver.find_elements(By.CSS_SELECTOR, "div.legend__value") 
                                for i in range(len(education_elements)):
                                    apply_education[education_elements[i].text] = education_values[i].text
                            except Exception as e:
                                apply_education = {}
                                logging.info(f"獲取聯絡方式時發生錯誤: {e}")
                            # 抓取性別分布
                            try:
                                gender = {}
                                gender_elements = driver.find_elements(By.CSS_SELECTOR, ".stack-bar__text__block")
                                for element in gender_elements[:2]:
                                    style = element.get_attribute("style")
                                    rgb_value = style[style.find("rgb"):style.find(")") + 1]
                                    gender_text = element.find_element(By.CSS_SELECTOR, "div").text
                                    # 定義目標RGB值
                                    male_rgb = [78, 145, 255]    # 藍色
                                    female_rgb = [255, 144, 199]  # 粉色
                                    if is_similar_rgb(rgb_value, male_rgb):
                                        gender["男性"] = gender_text
                                    elif is_similar_rgb(rgb_value, female_rgb):
                                        gender["女性"] = gender_text
                            except Exception as e:
                                gender = {}
                                logging.info(f"獲取性別分布時發生錯誤: {e}")
                            # 抓取語言能力
                            try:
                                # 選取div.chart-container__body的第5個是下下之策
                                language_container = driver.find_elements(By.CSS_SELECTOR, "div.chart-container__body")[5]
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
                                            logging.info(f"提取{language_name}技能等級時出錯: {e}")
                                    # 將語言技能加入字典
                                    language_skills[language_name] = ','.join(language_description)
                            except Exception as e:
                                language_skills = {}
                                logging.info(f"獲取語言能力時發生錯誤: {e}")
                            
                            # 主要處理邏輯
                            # 定位所有的圖表容器
                            try:
                                chart_containers = driver.find_elements(By.CSS_SELECTOR, 'div.chart-container.d-flex.flex-column.bg-white.overflow-hidden.horizontal-bar-chart')
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
                                                logging.info(f"獲取年齡分佈時發生錯誤: {e}")
                                                age_distribution = {}
                                        elif title == '工作經驗':
                                            try:
                                                work_experience = extracted_data
                                            except Exception as e:
                                                logging.info(f"獲取工作經驗分佈時發生錯誤: {e}")
                                                work_experience = {}
                                        elif title == '科系':
                                            try:
                                                major_distribution = extracted_data
                                            except Exception as e:
                                                logging.info(f"獲取科系分佈時發生錯誤: {e}")
                                                major_distribution = {}
                                        elif title == '技能':
                                            try:
                                                skills_distribution = extracted_data
                                            except Exception as e:
                                                logging.info(f"獲取技能分佈時發生錯誤: {e}")
                                                skills_distribution = {}
                                        elif title == '證照':
                                            try:
                                                certificates_distribution = extracted_data
                                            except Exception as e:
                                                logging.info(f"獲取證照分佈時發生錯誤: {e}")
                                                certificates_distribution = {}
                                        else:
                                            logging.info(f"未知的標題: {title}")
                                    else:
                                        logging.info(f"未知的標題: {title}")
                            except Exception as e:
                                logging.error(f"獲取應徵眾多資訊時發生錯誤: {e}")
                        except Exception as e:
                            logging.error(f"獲取應徵詳細資訊時發生錯誤: {e}")
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
                        try:
                            job_list.append({
                                "job_id":apply_code+update_date,
                                "job_name":job_name, "company_name":company, "update_date":update_date, "actively_hiring":actively_hiring, 
                                "applicants":applicants, "job_description":job_description, "job_category":job_category, "salary":salary, "job_type":job_type, 
                                "location":location, "management":management, "business_trip":business_trip, "work_time":work_time, "vacation":vacation, 
                                "start_work":start_work, "headcount":headcount, "work_exp":work_exp, "education":education, "major":major, 
                                "language":language, "skills":skills, "certificates":certificates, "other_requirements":other_requirements,
                                "legal_benefits":legal_benefits_str, "other_benefits":other_benefits_str, "raw_benefits":raw_benefits, "contact_info":contact_info_str,
                                "apply_education":apply_education, "apply_gender": gender, "apply_language": language_skills, "apply_age_distribution": age_distribution,
                                "apply_experience": work_experience, "apply_major": major_distribution, "apply_skills": skills_distribution, "apply_certificates": certificates_distribution,
                                "status": "active"                     
                            })
                            # job_id INT REFERENCES jobs(job_id),
                            # tools_id INT REFERENCES tools(tools_id),
                            # PRIMARY KEY (job_id, tool_id)
                            job_id = apply_code+update_date
                            # tools_id = None
                            # 遍歷工具列表，並將每個工具添加到 tools_list
                        except Exception as e:
                            logging.error(f"處理職缺時發生錯誤: {e}")
                        try:
                            if tools != "":
                                # 將工具字串轉換為列表
                                tools = tools.split("、")  # 使用 "、" 分隔符
                                for tool in tools:
                                    # tools_id = f"tool_{index + 1}"  # 根據索引生成 tool_id
                                    tools_list.append({"job_id": job_id, "tool": tool})
                            else:
                                tools_list.clear()
                                tools_list.append({"job_id": job_id, "tool": tools})
                        except Exception as e:
                            tools_list.clear()
                            logging.error(f"處理工具列表時發生錯誤: {e}")
                            tools_list.append({"job_id": job_id, "tool": tools})
                        # 使用 split() 方法分割字符串
                        try:
                            # 將公司網址中的公司 ID 提取出來
                            logging.info(f"公司網址: {company_url}")
                            # 以 "/" 分割 URL，將結果存成串列
                            parts = company_url.split('/')
                            # 分割結果的最後一部分可能包含 query 參數，所以以 "?" 進一步分割
                            if len(parts) >= 5:
                                # 以下假設 URL 格式為 "https://www.104.com.tw/company/ID?..."
                                company_id = parts[4].split('?')[0]
                                com_list.append({"company_url":company_url, "company_id":company_id})  
                            else:
                                raise ValueError("URL 格式錯誤: " + company_url)
                        except Exception as e:
                            logging.error(f"處理公司網址時發生錯誤: {e}")
                        job_count+=1
                    except Exception as e:
                        logging.error(f"處理詳細頁面資訊時發生錯誤: {e}")
                        job_list.append({
                            "job_id":apply_code+update_date,
                            "job_name":job_name, "company_name":company, "update_date":update_date, "actively_hiring":actively_hiring, 
                            "applicants":"", "job_description": "", "job_category": "", "salary": "", "job_type": "",
                            "location": "", "management": "", "business_trip": "", "work_time": "",
                            "vacation": "", "start_work": "", "headcount": "", "work_exp": "", "education": "", 
                            "major":"", "language":"", "skills":"", "certificates":"", 
                            "other_requirements":"", "legal_benefits":"", "other_benefits":"", "raw_benefits":"", "contact_info":"", "status": "draft",
                            "apply_education":{}, "apply_gender": {}, "apply_language": {}, "apply_age_distribution": {},
                            "apply_experience": {}, "apply_major": {}, "apply_skills": {}, "apply_certificates": {}
                            # 新增欄位的空值
                        })
                        job_url_list.append({"job_id": apply_code+update_date, "job_url":job_url})              
                        com_list.append([""])
                        # tools_id = None
                        tools_list.append({"job_id": apply_code+update_date, "tool": tools})
                        job_count +=1
                        if sum(1 for field in job_list[-1] if field == "") > 6:
                            crawler_error += 1
                    # 關閉詳細頁面，切回列表頁
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    # 儲存資料
                    try:
                        x_save(job_list, job_count= job_count,directory='D:/allm/crawler/job_list', keyword = keyword, table_name='jobs')
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"com_url_{timestamp}.json"
                        x_save(com_list, job_count= job_count,filename = filename ,directory='D:/allm/crawler/com_url', keyword = keyword, table_name="com_url")
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"tools_list_{timestamp}.json"
                        x_save(tools_list, job_count= job_count,filename=filename,directory='D:/allm/crawler/tools', keyword = keyword, table_name='job_tools')
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"job_url_{timestamp}.json"
                        x_save(job_url_list, job_count= job_count,filename=filename,directory='D:/allm/crawler/job_url', keyword = keyword, table_name='job_url')
                    except Exception as e:
                        logging.error(f"儲存時發生錯誤: {e}")
                except Exception as e:
                    logging.error(f"處理 {company}, {job_name}職缺時發生錯誤, {job_url}: {e}")
                    crawler_error += 1
                    job_count +=1
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    # 儲存資料
                    x_save(job_list, job_count = job_count,directory='D:/allm/crawler/job_list', keyword = keyword, table_name='jobs')
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"com_url_{timestamp}.json"
                    x_save(com_list, job_count = job_count,filename = filename ,directory='D:/allm/crawler/com_url', keyword = keyword, table_name="com_url")
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"tools_list_{timestamp}.json"
                    x_save(tools_list, job_count = job_count,filename = filename ,directory='D:/allm/crawler/tools', keyword = keyword, table_name='job_tools')
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"job_url_{timestamp}.json"
                    x_save(job_url_list, job_count = job_count,filename = filename ,directory='D:/allm/crawler/job_url', keyword = keyword, table_name='job_url')
                    continue
            else:
                try:
                    # 若錯誤次數超過上限，則不再處理新的任務
                    if job_count > 3:
                        unprocessed_jobs = current_jobs[job_count-3:]
                    else:
                        unprocessed_jobs = current_jobs
                    logging.error("錯誤次數超過上限，停止處理後續職缺")
                    with open('D:/allm/crawler/undo/unprocessed_jobs.json', 'w', encoding='utf-8') as f:
                        json.dump(unprocessed_jobs, f, ensure_ascii=False, indent=4)
                except Exception as e:
                    logging.error(f"錯誤處理時發生錯誤: {e}")
        current_jobs = []
        unprocessed_jobs = []
    while True:
        if len(unprocessed_jobs) > 0:
            logging.info("處理未完成的職缺")
            extract_job_info(unprocessed_jobs)
        elif len(current_jobs) > 0:
            logging.info("處理職缺中")
            extract_job_info(current_jobs)
        else:
            logging.info("沒有職缺可以處理")
            break
    logging.info("已處理完所有職缺")
keyword_list = ["電子工程師", "電力工程師", "電源工程師", "數位IC設計工程師", "類比IC設計工程師", "IC佈局工程師", "半導體工程師", "光學工程師", "熱傳工程師"]
# 使用方式
crawl_jobs(keyword_list, max_errors=3, max_scrolls=100000)
if len(job_list) > 0:
    save_to_json(raw_data= job_list, directory='D:/allm/crawler/job_list')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"com_url_{timestamp}.json"
    save_to_json(raw_data= com_list,filename=filename, directory='D:/allm/crawler/com_url')
    # save_to_json(raw_data= applicants_analysis, directory='D:/allm/crawler/applicants_analysis')
    upload_data(data=job_list, table_name='jobs')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"tools_list_{timestamp}.json"
    upload_data(data=tools_list, table_name='job_tools')
driver.quit()
logging.info("職缺爬蟲程式執行完畢")
# 關鍵字
'''
資訊軟體系統類
keyword_list = ["iOS 工程師", "Android 工程師", "前端工程師", "後端工程師", "全端工程師", "數據分析師", "軟體工程師", "軟體助理工程師", "軟體專案主管", "系統分析師", "資料科學家", "資料工程師", "AI工程師", "演算法工程師", "韌體工程師", "電玩程式設計師", "Internet程式設計師", "資訊助理", "區塊鏈工程師", "BIOS工程師", "通訊軟體工程師", "電子商務技術主管", "其他資訊專業人員", "系統工程師", "網路管理工程師", "資安工程師", "資訊設備管制人員", "雲端工程師", "網路安全分析師", "MES工程師", "MIS程式設計師", "資料庫管理人員", "MIS / 網管主管", "資安主管"]
研發相關
keyword_list = [
"iOS 工程師", "Android 工程師", "前端工程師", "後端工程師", "全端工程師", "數據分析師", "軟體工程師", "軟體助理工程師", "軟體專案主管", "系統分析師", "資料科學家", "資料工程師", "AI工程師", "演算法工程師", "韌體工程師", "電玩程式設計師", "Internet程式設計師", "資訊助理", "區塊鏈工程師", "BIOS工程師", "通訊軟體工程師", "電子商務技術主管", "其他資訊專業人員", "系統工程師", "網路管理工程師", "資安工程師", "資訊設備管制人員", "雲端工程師", "網路安全分析師", "MES工程師", "MIS程式設計師", "資料庫管理人員", "MIS / 網管主管", "資安主管"
# 研發相關
"助理工程師", "工程助理", "機構工程師", "機械工程師", "電子工程師", "電力工程師", "電源工程師", "數位IC設計工程師", "類比IC設計工程師", "IC佈局工程師", "半導體工程師", "光學工程師", "熱傳工程師", "零件工程師", "光電工程師", "光電工程研發主管", "RF通訊工程師", "電信/通訊系統工程師", "通訊工程研發主管", "太陽能技術工程師", "PCB佈線工程師", "硬體研發工程師", "硬體工程研發主管", "電子產品系統工程師", "微機電工程師", "聲學/噪音工程師", "機電技師/工程師", "電機技師/工程師", "其他特殊工程師", "其他工程研發主管", "材料研發人員", "化工化學工程師", "實驗化驗人員", "特用化學工程師", "紡織化學工程師", "生物科技研發人員", "醫藥研發人員", "醫療器材研發工程師", "食品研發人員", "化學工程研發人員", "病理藥理研究人員", "農藝/畜產研究人員",
# 生物醫療
'醫事檢驗師', '藥師', '營養師', '公共衛生醫師', '麻醉醫師', '復健技術師', '治療師', '醫事放射師', '牙醫師', '護理師', '獸醫師', '中醫師', '驗光師', '呼吸治療師', '職能治療師', '物理治療師', '語言治療師', '專科治療師', '牙體治療', '心理師', '放射性設備使用技術員', '醫療設備控制人員',
# 金融
'銀行辦事員', '證券營業員', '理財專員', '金融交易員', '金融營業員', '金融承銷員', '金融研究員', '金融主管', '保險業務/經紀人', '保險主管', '融資/信用業務人員', '核保/保險內勤人員', '理賠人員', '股務人員', '催收人員', '券商後線人員', '統計精算人員', '投資經理人', '風險管理人員', '不動產估價師', '記帳/出納/一般會計', '主辦會計', '成本會計', '財務會計助理', '財務分析/財務人員', '財務或會計主管', '稽核人員', '稽核主管', '會計師', '查帳/審計人員', '財務長', '記帳士', '稅務人員',
# 製造
'自動控制工程師', '生產設備工程師', 'SMT工程師', '半導體製程工程師', '半導體設備工程師', 'LCD製程工程師', 'LCD設備工程師', '生產技術/製程工程師', '軟韌體測試工程師', '可靠度工程師', '測試人員', '硬體測試工程師', 'EMC / 電子安規工程師', 'IC封裝/測試工程師', '品管/檢驗人員', '品管/品保工程師', 'ISO/品保人員', '品管/品保主管', '故障分析工程師',
]
牙體治療, 心理師, 醫療設備控制人員, 呼吸治療師, 專科治療師, 語言治療師, 物理治療師, 職能治療師, 驗光師,中醫師, '醫事檢驗師', 

keyword_list = ['後端工程師'] #觀察變化
'''