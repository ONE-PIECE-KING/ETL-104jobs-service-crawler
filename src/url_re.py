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
from dotenv import load_dotenv
import logging
import socket
import glob

# ------------------ 設定參數 -------------------
target_jobs = []  # 如果為空，則抓取所有職缺
target_primary_category = []  # 如果為空，則抓取所有次要分類
target_industry = ["資訊軟體系統類"]  # 目標產業
target_district = [] #金山瑞芳各1
target_city = []
target_continent = ['台灣地區']

nouxe_jobs = []  # 不需要的職缺
nouxe_primary_category = []  # 不需要的次要分類
nouxe_industry = []  # 不需要的產業
nouse_district = ["新北市萬里區", "新北市金山區", "新北市平溪區", "新北市貢寮區", "新北市金山區", 
                   "新北市瑞芳區", "新北市烏來區", "新北市石門區", "宜蘭縣頭城鎮", "宜蘭縣礁溪鄉", 
                   "宜蘭縣壯圍鄉", "宜蘭縣員山鄉", "宜蘭縣三星鄉", "宜蘭縣大同鄉", "宜蘭縣冬山鄉", 
                   "宜蘭縣南澳鄉", "基隆市安樂區"]  # 不需要的行政區
nouse_city = ["金門縣", "連江縣", "澎湖縣", "台東縣"]  # 不需要的地區 台東7
nouse_continent = []  # 不需要的洲



# 定義等待超時時間（以秒為單位）
WAIT_TIMEOUT = 10

# 存儲搜索結果的URL
search_urls = []

# ------------------------------------------------

"""初始化logging，預設log位址為logs/"""
def setup_logging(log_dir='logs'):
    # 確保日誌目錄存在
    os.makedirs(log_dir, exist_ok=True)
    # 產生日誌檔名（使用當前日期時間）
    log_filename = os.path.join(log_dir, f'url_collector_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    # 創建 logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # 修改为INFO级别
    # 清除之前的 handlers（防止重複日誌）
    logger.handlers.clear()
    # 創建文件 handler
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.INFO)  # 修改为INFO级别
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    # 創建控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # 控制台保持INFO级别
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    # 添加 handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logging.info("日志系统初始化完成，INFO級別已啟用")
    return log_filename

"""根據當前狀況選擇一個可用的連接埠"""
def get_available_port(start=9222, end=9322):
    """從指定範圍中尋找一個可用的連接埠"""
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    logging.error("無法找到可用的連接埠!")
    raise RuntimeError("沒有可用的連接埠!")

"""儲存_存到 json"""
def save_to_json(data, filename, directory='url_results'):
    """
    將數據存成 JSON 檔案
    :param data: 要保存的數據列表
    :param filename: 檔名
    :param directory: 存放位置，預設為 'url_results'
    """
    logging.info(f"準備保存數據到JSON，檔名: {filename}, 數據量: {len(data)} 項")
    # 確保檔名以 .json 結尾
    if not filename.endswith('.json'):
        filename += '.json'
    # 確保目錄存在
    full_dir_path = os.path.join('D:/allm/crawler', directory)
    if not os.path.exists(full_dir_path):
        logging.info(f"目錄 {full_dir_path} 不存在，正在創建")
        os.makedirs(full_dir_path)
    # 完整的檔案路徑
    file_path = os.path.join(full_dir_path, filename)
    try:
        # 使用 UTF-8 編碼寫入 JSON 檔案
        logging.info(f"正在寫入數據到 {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info(f"資料已成功儲存至 {file_path}")
        return file_path
    except Exception as e:
        logging.error(f"儲存 JSON 檔案時發生錯誤: {e}")
        return None

"""將多個JSON檔案合併為一個"""
def merge_json_files(city_name, pattern='url_temp_*.json', output_filename=None, directory='url_results'):
    """
    合併指定目錄下符合模式的JSON檔案
    :param city_name: 城市名稱，用於生成輸出檔名
    :param pattern: 要合併的檔案模式
    :param output_filename: 輸出檔名，若為None則自動生成
    :param directory: 檔案所在目錄
    :return: 合併後的檔案路徑
    """
    logging.info(f"開始合併 {city_name} 的JSON文件，模式: {pattern}")
    full_dir_path = os.path.join('D:/allm/crawler', directory)
    # 獲取所有符合pattern的文件
    file_pattern = os.path.join(full_dir_path, pattern)
    files = glob.glob(file_pattern)
    
    if not files:
        logging.warning(f"沒有找到符合模式 {pattern} 的文件")
        return None
    
    logging.info(f"找到 {len(files)} 個符合條件的文件，準備合併")
    # 如果沒有指定輸出檔名，則使用城市名稱和時間戳生成
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"search_urls_{city_name}_{timestamp}.json"
        logging.info(f"自動生成輸出檔名: {output_filename}")
    
    # 合併數據
    merged_data = []
    for file in files:
        try:
            logging.info(f"正在處理文件: {file}")
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    logging.info(f"從文件 {file} 中讀取到 {len(data)} 項數據")
                    merged_data.extend(data)
                else:
                    logging.info(f"從文件 {file} 中讀取到單個數據項")
                    merged_data.append(data)
            # 合併後刪除臨時文件
            logging.info(f"正在刪除臨時文件: {file}")
            os.remove(file)
            logging.info(f"已處理並刪除臨時文件: {file}")
        except Exception as e:
            logging.error(f"處理文件 {file} 時發生錯誤: {e}")
    
    # 保存合併後的數據
    if merged_data:
        logging.info(f"合併完成，共 {len(merged_data)} 項數據，準備保存到 {output_filename}")
        return save_to_json(merged_data, output_filename, directory)
    else:
        logging.warning("沒有數據可以合併")
        return None

"""初始化driver"""
def setup_driver():
    logging.info("開始初始化WebDriver")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('--start-maximized')
    # 注意要修改，偵測port可使用
    available_port = get_available_port()
    chrome_options.add_argument(f'--remote-debugging-port={available_port}')
    chrome_options.add_argument('--disable-gpu')
    
    ua = UserAgent()
    random_ua = ua.random
    chrome_options.add_argument(f'user-agent={random_ua}')
    
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

def collect_urls(filename=None):
    logging.info("开始收集URL")
    logging.info(f"初始化WebDriver，準備訪問104人力銀行")
    driver = setup_driver()
    logging.info("浏览器驱动初始化完成")
    base_url = "https://www.104.com.tw/jobs/search"
    logging.info(f"准备访问网站: {base_url}")
    driver.get(base_url)
    time.sleep(3)
    logging.info("頁面已加載，準備開始操作")
    logging.info("网站加载完成")
    # 定义选择器变量
    lv1_selector = '//li[contains(@class, "category-item") and contains(@class, "category-item--level-one")]'
    lv2_selector = '//li[contains(@class, "category-item") and contains(@class, "category-item--level-two")]'
    lv3_selector = '//li[contains(@class, "category-item") and contains(@class, "category-item--level-three")]'
    # 定义CSS选择器变量
    area_btn_selector = "button[data-gtm-joblist='搜尋欄位-地區']"
    industry_btn_selector = "button[data-gtm-joblist='搜尋欄位-職類']"
    search_btn_selector = "button[data-gtm-joblist='搜尋欄位-搜尋點擊']"
    confirm_btn_selector = "button.category-picker-btn-primary"
    # 临时存储URL的列表和计数器
    temp_urls = []
    url_count = 0
    total_urls = 0
    city_urls_files = []
    # 點擊地區按鍵,以彈出地區選擇視窗
    logging.info("準備點擊地區按鈕")
    area_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, area_btn_selector)))
    area_btn.click()
    time.sleep(3)
    logging.info("地區選擇視窗已打開")
    # 選擇洲別continent
    logging.info("獲取所有洲別元素")
    continent_elements = driver.find_elements(By.XPATH, lv1_selector)
    continent_elements_text = [continent.text for continent in continent_elements]
    logging.info(f"找到以下洲別: {continent_elements_text}")
    
    continent_process_count = 0
    for continent_index in range(len(continent_elements)):
        current_continent = continent_elements_text[continent_index]
        
        # 檢查是否需要處理該洲
        if target_continent and current_continent not in target_continent:
            logging.info(f"跳過洲別 {current_continent}，因為其不在 target_continent 列表中")
            continue
        if nouse_continent and current_continent in nouse_continent:
            logging.info(f"跳過洲別 {current_continent}，因為其在 nouse_continent 列表中")
            continue
            
        logging.info(f"開始處理洲別: {current_continent} ({continent_index+1}/{len(continent_elements)})")
        logging.info(f"重新獲取洲別元素列表")
        if continent_process_count ==0:
            logging.info(f"點擊洲別: {current_continent}")
            continent_elements = driver.find_elements(By.XPATH, lv1_selector)
            continent_elements_text = [continent.text for continent in continent_elements]            
            continent_elements[continent_index].click()
            time.sleep(3)
        else:
            logging.info("重新打開地區選擇視窗")
            area_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, area_btn_selector)))
            area_btn.click()
            time.sleep(3)
            logging.info("重新獲取洲別元素")
            continent_elements = driver.find_elements(By.XPATH, lv1_selector)
            continent_elements_text = [continent.text for continent in continent_elements]
            logging.info(f"點擊洲別: {current_continent}")
            continent_elements[continent_index].click()
            time.sleep(3)
        continent_process_count +=1    
        #  選擇縣市city
        logging.info(f"獲取 {current_continent} 下的所有縣市")
        city_elements = driver.find_elements(By.XPATH, lv2_selector)
        city_elements_text = [city.text for city in city_elements]
        logging.info(f"找到以下縣市: {city_elements_text}")
        city_process_count = 0
        for city_index in range(len(city_elements)):
            city_name = city_elements_text[city_index]
            
            # 檢查是否需要處理該城市
            if target_city and city_name not in target_city:
                logging.info(f"跳過城市 {city_name}，因為其不在 target_city 列表中")
                continue
            if nouse_city and city_name in nouse_city:
                logging.info(f"跳過城市 {city_name}，因為其在 nouse_city 列表中")
                continue
                
            logging.info(f"開始處理城市: {city_name} ({city_index+1}/{len(city_elements)})")
            # 重置當前城市的URL計數和臨時列表
            city_url_count = 0
            city_temp_urls = []
            
            if city_process_count ==0:
                logging.info(f"點擊城市: {city_name}")
                city_elements = driver.find_elements(By.XPATH, lv2_selector)
                city_elements_text = [city.text for city in city_elements]                
                city_elements[city_index].click()
                time.sleep(3)
            else:
                logging.info("重新打開地區選擇視窗")
                area_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, area_btn_selector)))
                area_btn.click()
                time.sleep(3)
                logging.info(f"重新選擇洲別: {current_continent}")
                continent_elements = driver.find_elements(By.XPATH, lv1_selector)
                continent_elements_text = [continent.text for continent in continent_elements]
                continent_elements[continent_index].click()
                time.sleep(3)
                logging.info("重新獲取城市列表")
                city_elements = driver.find_elements(By.XPATH, lv2_selector)
                city_elements_text = [city.text for city in city_elements]
                logging.info(f"點擊城市: {city_name}")
                city_elements[city_index].click()
                time.sleep(3)
            city_process_count +=1
            # 選擇區縣district
            logging.info(f"獲取 {city_name} 下的所有行政區")
            district_elements = driver.find_elements(By.XPATH, lv3_selector)
            district_elements_text = [district.text for district in district_elements]
            logging.info(f"找到以下行政區: {district_elements_text}")
            
            # 找出有效行政區块的起始和结束索引
            start_index = -1
            end_index = -1
            
            # 确定有效内容的起始索引
            for i, text in enumerate(district_elements_text):
                if text.strip():
                    if start_index == -1:
                        start_index = i
                    end_index = i
            
            if start_index != -1 and end_index != -1:
                logging.info(f"有效行政區块的起始索引: {start_index}, 結束索引: {end_index}")
                logging.info(f"有效行政區數量: {end_index - start_index + 1}")
                
                # 只处理有效范围内的行政区
                district_process_count = 0
                for district_index in range(start_index, end_index + 1):
                    current_district = district_elements_text[district_index]
                    
                    # 檢查是否需要處理該行政區
                    if target_district and current_district not in target_district:
                        logging.info(f"跳過行政區 {current_district}，因為其不在 target_district 列表中")
                        continue
                    if nouse_district and current_district in nouse_district:
                        logging.info(f"跳過行政區 {current_district}，因為其在 nouse_district 列表中")
                        continue
                        
                    logging.info(f"開始處理行政區: {current_district} ({district_index - start_index + 1}/{end_index - start_index + 1})")
                    if district_process_count == 0:
                        logging.info(f"點擊行政區: {current_district}")
                        district_elements = driver.find_elements(By.XPATH, lv3_selector)
                        district_elements_text = [district.text for district in district_elements]                    
                        district_elements[district_index].click()
                        time.sleep(3)
                    else:
                        logging.info("重新打開地區選擇視窗")
                        area_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, area_btn_selector)))
                        area_btn.click()
                        time.sleep(3)
                        logging.info(f"重新選擇洲別: {current_continent}")
                        continent_elements = driver.find_elements(By.XPATH, lv1_selector)
                        continent_elements_text = [continent.text for continent in continent_elements]
                        continent_elements[continent_index].click()
                        time.sleep(3)
                        logging.info(f"重新選擇城市: {city_name}")
                        city_elements = driver.find_elements(By.XPATH, lv2_selector)
                        city_elements_text = [city.text for city in city_elements]
                        city_elements[city_index].click()
                        time.sleep(3)
                        logging.info(f"重新獲取行政區列表")
                        district_elements = driver.find_elements(By.XPATH, lv3_selector)
                        district_elements_text = [district.text for district in district_elements]
                        
                        # 重新计算有效区块
                        start_index = -1
                        end_index = -1
                        for i, text in enumerate(district_elements_text):
                            if text.strip():
                                if start_index == -1:
                                    start_index = i
                                end_index = i
                        
                        logging.info(f"點擊行政區: {current_district}")
                        district_elements[district_index].click()
                        time.sleep(3)
                    district_process_count += 1
                    
                    logging.info("點擊確認按鈕")
                    confirm_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, confirm_btn_selector)))
                    confirm_btn.click()
                    time.sleep(3)
                    logging.info("地區選擇已確認")
                    
                    # 點擊職類按鍵,以彈出職類選擇視窗
                    logging.info("準備點擊職類按鈕")
                    industry_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, industry_btn_selector)))
                    industry_btn.click()
                    time.sleep(3)
                    logging.info("職類選擇視窗已打開")

                    # 選擇主要分類
                    logging.info("獲取所有主要職類元素")
                    industry_elements = driver.find_elements(By.XPATH, lv1_selector)
                    industry_elements_text = [industry.text for industry in industry_elements]
                    logging.info(f"找到以下主要職類: {industry_elements_text}")
                    
                    industry_process_count = 0
                    for industry_index in range(len(industry_elements)):
                        current_industry = industry_elements_text[industry_index]
                        
                        # 檢查是否需要處理該行業
                        if target_industry and current_industry not in target_industry:
                            logging.info(f"跳過行業 {current_industry}，因為其不在 target_industry 列表中")
                            continue
                        if nouxe_industry and current_industry in nouxe_industry:
                            logging.info(f"跳過行業 {current_industry}，因為其在 nouxe_industry 列表中")
                            continue
                            
                        logging.info(f"開始處理主要職類: {current_industry} ({industry_index+1}/{len(industry_elements)})")
                        if industry_process_count == 0:
                            logging.info(f"點擊主要職類: {current_industry}")
                            industry_elements = driver.find_elements(By.XPATH, lv1_selector)
                            industry_elements_text = [industry.text for industry in industry_elements]                        
                            industry_elements[industry_index].click()
                            time.sleep(3)
                        else:
                            logging.info("重新打開職類選擇視窗")
                            industry_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, industry_btn_selector)))
                            industry_btn.click()
                            time.sleep(3)
                            logging.info("重新獲取主要職類元素")
                            industry_elements = driver.find_elements(By.XPATH, lv1_selector)
                            industry_elements_text = [industry.text for industry in industry_elements]
                            logging.info(f"點擊主要職類: {current_industry}")
                            industry_elements[industry_index].click()
                            time.sleep(3)
                        industry_process_count += 1
                        # 選擇次要分類
                        logging.info(f"獲取 {current_industry} 下的所有次要分類")
                        primary_category_elements = driver.find_elements(By.XPATH, lv2_selector)
                        primary_category_elements_text = [primary_category.text for primary_category in primary_category_elements]
                        logging.info(f"找到以下次要分類: {primary_category_elements_text}")
                        
                        primary_category_process_count = 0
                        for primary_category_index in range(len(primary_category_elements)):
                            current_primary_category = primary_category_elements_text[primary_category_index]
                            
                            # 檢查是否需要處理該次要分類
                            if target_primary_category and current_primary_category not in target_primary_category:
                                logging.info(f"跳過次要分類 {current_primary_category}，因為其不在 target_primary_category 列表中")
                                continue
                            if nouxe_primary_category and current_primary_category in nouxe_primary_category:
                                logging.info(f"跳過次要分類 {current_primary_category}，因為其在 nouxe_primary_category 列表中")
                                continue
                                
                            logging.info(f"開始處理次要分類: {current_primary_category} ({primary_category_index+1}/{len(primary_category_elements)})")
                            if primary_category_process_count == 0:
                                logging.info(f"點擊次要分類: {current_primary_category}")
                                primary_category_elements = driver.find_elements(By.XPATH, lv2_selector)
                                primary_category_elements_text = [primary_category.text for primary_category in primary_category_elements]                            
                                primary_category_elements[primary_category_index].click()
                                time.sleep(3)
                            else:
                                logging.info("重新打開職類選擇視窗")
                                industry_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, industry_btn_selector)))
                                industry_btn.click()
                                time.sleep(3)
                                logging.info(f"重新選擇主要職類: {current_industry}")
                                industry_elements = driver.find_elements(By.XPATH, lv1_selector)
                                industry_elements_text = [industry.text for industry in industry_elements]
                                industry_elements[industry_index].click()
                                time.sleep(3)
                                logging.info("重新獲取次要分類元素")
                                primary_category_elements = driver.find_elements(By.XPATH, lv2_selector)
                                primary_category_elements_text = [primary_category.text for primary_category in primary_category_elements]
                                logging.info(f"點擊次要分類: {current_primary_category}")
                                primary_category_elements[primary_category_index].click()
                                time.sleep(3)
                            primary_category_process_count += 1
                            # 選擇職務
                            logging.info(f"獲取 {current_primary_category} 下的所有職務")
                            
                            # 获取当前选中的分类下的level-three-area容器
                            # 注意：这里只获取当前可见的level-three-area容器
                            all_job_areas = driver.find_elements(By.XPATH, '//ul[contains(@class, "level-three-area") and @data-open="true"]')
                            logging.info(f"当前分类下找到 {len(all_job_areas)} 个可见的level-three-area容器")
                            
                            # 只处理当前可见的容器内的职务
                            for area_index, job_area in enumerate(all_job_areas):
                                logging.info(f"处理第 {area_index+1}/{len(all_job_areas)} 个level-three-area容器")
                                
                                # 获取当前容器内的职务元素
                                job_elements = job_area.find_elements(By.XPATH, './/li[contains(@class, "category-item") and contains(@class, "category-item--level-three")]')
                                job_elements_text = [job.text for job in job_elements]
                                logging.info(f"当前容器中找到 {len(job_elements)} 个职务: {job_elements_text}")
                                
                                # 筛选要处理的职务
                                filtered_job_indices = []
                                for job_index, job_text in enumerate(job_elements_text):
                                    if target_jobs and job_text not in target_jobs:
                                        logging.info(f"跳過職務 {job_text}，因為其不在 target_jobs 列表中")
                                        continue
                                    if nouxe_jobs and job_text in nouxe_jobs:
                                        logging.info(f"跳過職務 {job_text}，因為其在 nouxe_jobs 列表中")
                                        continue
                                    filtered_job_indices.append(job_index)
                                
                                logging.info(f"過濾後將處理 {len(filtered_job_indices)} 個職務")
                                
                                # 处理当前容器内的每个职务
                                job_process_count = 0
                                for job_index in filtered_job_indices:
                                    current_job = job_elements_text[job_index]
                                    logging.info(f"開始處理職務: {current_job} ({job_index+1}/{len(job_elements)})")
                                    
                                    if job_process_count == 0:
                                        logging.info(f"點擊職務: {current_job}")
                                        # 重新获取当前容器内的元素并点击
                                        job_elements = job_area.find_elements(By.XPATH, './/li[contains(@class, "category-item") and contains(@class, "category-item--level-three")]')
                                        job_elements[job_index].click()
                                        time.sleep(3)
                                    else:
                                        logging.info("重新打開職類選擇視窗")
                                        industry_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, industry_btn_selector)))
                                        industry_btn.click()                                    
                                        time.sleep(3)
                                        logging.info(f"重新選擇主要職類: {current_industry}")
                                        industry_elements = driver.find_elements(By.XPATH, lv1_selector)
                                        industry_elements_text = [industry.text for industry in industry_elements]
                                        industry_elements[industry_index].click()
                                        time.sleep(3)
                                        logging.info(f"重新選擇次要分類: {current_primary_category}")
                                        primary_category_elements = driver.find_elements(By.XPATH, lv2_selector)
                                        primary_category_elements_text = [primary_category.text for primary_category in primary_category_elements]
                                        primary_category_elements[primary_category_index].click()
                                        time.sleep(3)
                                        
                                        logging.info("重新獲取職務元素")
                                        # 重新获取当前可见的level-three-area容器
                                        all_job_areas = driver.find_elements(By.XPATH, '//ul[contains(@class, "level-three-area") and @data-open="true"]')
                                        if area_index < len(all_job_areas):
                                            job_area = all_job_areas[area_index]
                                            job_elements = job_area.find_elements(By.XPATH, './/li[contains(@class, "category-item") and contains(@class, "category-item--level-three")]')
                                            logging.info(f"點擊職務: {current_job}")
                                            job_elements[job_index].click()
                                            time.sleep(3)
                                        else:
                                            logging.error(f"无法找到第 {area_index+1} 个level-three-area容器")
                                            continue
                                    
                                    job_process_count += 1
                                    logging.info("點擊確認按鈕")
                                    confirm_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, confirm_btn_selector)))
                                    confirm_btn.click()
                                    time.sleep(3)
                                    logging.info("職類選擇已確認")

                                    # 點擊搜尋按鍵
                                    logging.info("點擊搜尋按鈕")
                                    search_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, search_btn_selector)))
                                    search_btn.click()
                                    time.sleep(3)
                                    logging.info("搜尋已執行")

                                    
                                    current_url = driver.current_url  # 開始獲取網址
                                    logging.info(f"獲取到搜尋結果URL: {current_url}")
                                    
                                    # 将URL和元素文本添加到结果中
                                    result = {
                                        "continent": continent_elements_text[continent_index],
                                        "city": city_elements_text[city_index],
                                        "district": district_elements_text[district_index],
                                        "industry": industry_elements_text[industry_index],
                                        "primary_category": primary_category_elements_text[primary_category_index],
                                        "job_title": current_job,
                                        "job_area_index": area_index,
                                        "job_local_index": job_index,
                                        "url": current_url
                                    }
                                    logging.info(f"組合結果數據: {result}")
                                    
                                    # 将结果添加到临时列表
                                    temp_urls.append(result)
                                    city_temp_urls.append(result)
                                    url_count += 1
                                    city_url_count += 1
                                    total_urls += 1
                                    logging.info(f"當前城市URL數: {city_url_count}, 總URL數: {total_urls}")
                                    
                                    # 每100个URL保存一次
                                    if city_url_count % 100 == 0:
                                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                        temp_filename = f"url_temp_{city_name}_{timestamp}.json"
                                        logging.info(f"達到100個URL，準備保存臨時文件: {temp_filename}")
                                        save_to_json(city_temp_urls, temp_filename)
                                        logging.info(f"已保存 {len(city_temp_urls)} 個URL到臨時文件 {temp_filename}")
                                        city_temp_urls = []
                                    
                                    # 清除產業查詢條件
                                    logging.info("清除產業查詢條件")
                                    industry_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, industry_btn_selector)))
                                    industry_btn.click()
                                    time.sleep(3)
                                    logging.info(f"清除產業查詢條件_選擇主要職類: {current_industry}")
                                    industry_elements = driver.find_elements(By.XPATH, lv1_selector)
                                    industry_elements[industry_index].click()
                                    time.sleep(3)
                                    logging.info(f"清除產業查詢條件_選擇次要分類: {current_primary_category}")
                                    primary_category_elements = driver.find_elements(By.XPATH, lv2_selector)
                                    primary_category_elements[primary_category_index].click()
                                    time.sleep(3)
                                    
                                    logging.info("清除產業查詢條件_獲取職務元素")
                                    # 重新获取当前可见的level-three-area容器
                                    all_job_areas = driver.find_elements(By.XPATH, '//ul[contains(@class, "level-three-area") and @data-open="true"]')
                                    if area_index < len(all_job_areas):
                                        job_area = all_job_areas[area_index]
                                        job_elements = job_area.find_elements(By.XPATH, './/li[contains(@class, "category-item") and contains(@class, "category-item--level-three")]')
                                        logging.info(f"清除產業查詢條件_點擊職務: {current_job}")
                                        job_elements[job_index].click()
                                        time.sleep(3)
                                    else:
                                        logging.error(f"清除条件时无法找到第 {area_index+1} 个level-three-area容器")
                                        continue
                                    
                                    logging.info("清除地區查詢條件_點擊確認按鈕")
                                    confirm_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, confirm_btn_selector)))
                                    confirm_btn.click()
                                    time.sleep(3)
                    
            # 当前城市处理完毕，保存剩余URL
            if city_temp_urls:
                logging.info(f"處理完 {current_district} 的所有職缺，保存剩余URL")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                temp_filename = f"url_temp_{city_name}_{timestamp}.json"
                save_to_json(city_temp_urls, temp_filename)
                logging.info(f"已保存剩余 {len(city_temp_urls)} 個URL到臨時文件 {temp_filename}")
            
            # 合并当前城市的所有临时文件
            logging.info(f"合併 {city_name} 的所有臨時文件")
            merged_file = merge_json_files(city_name, pattern=f"url_temp_{city_name}_*.json")
            if merged_file:
                city_urls_files.append(merged_file)
                logging.info(f"已合併城市 {city_name} 的所有URL到文件 {merged_file}")
            
            # 清除地區選擇條件
            logging.info(f"完成處理城市 {city_name}，清除地區查詢條件")
            area_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, area_btn_selector)))
            area_btn.click()
            time.sleep(3)
            logging.info(f"清除地區查詢條件_選擇洲別: {current_continent}")
            continent_elements = driver.find_elements(By.XPATH, lv1_selector)
            continent_elements[continent_index].click()
            time.sleep(3)
            logging.info(f"清除地區查詢條件_選擇城市: {city_name}")
            city_elements = driver.find_elements(By.XPATH, lv2_selector)
            city_elements[city_index].click()
            time.sleep(3)
            
            # 重新获取区县列表并计算有效块范围
            district_elements = driver.find_elements(By.XPATH, lv3_selector)
            district_elements_text = [district.text for district in district_elements]
            
            # 确定有效内容的起始索引
            start_index = -1
            end_index = -1
            for i, text in enumerate(district_elements_text):
                if text.strip():
                    if start_index == -1:
                        start_index = i
                    end_index = i
            
            if start_index <= district_index <= end_index:
                logging.info(f"清除地區查詢條件_選擇區縣: {district_elements_text[district_index]}")
                district_elements[district_index].click()
                time.sleep(3)
            else:
                logging.warning(f"district_index ({district_index}) 超出有效範圍 ({start_index}-{end_index})，使用第一個有效行政區")
                district_elements[start_index].click()
                time.sleep(3)
                
            logging.info("清除地區查詢條件_點擊確認按鈕")
            confirm_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, confirm_btn_selector)))
            confirm_btn.click()
            time.sleep(3)
    
    # 所有城市处理完毕，合并所有城市文件（如果需要）
    if len(city_urls_files) > 1 and filename:
        logging.info(f"所有城市處理完畢，開始合併所有城市文件，共 {len(city_urls_files)} 個文件")
        # 读取所有城市文件并合并
        all_urls = []
        for city_file in city_urls_files:
            try:
                logging.info(f"讀取城市文件: {city_file}")
                with open(city_file, 'r', encoding='utf-8') as f:
                    city_data = json.load(f)
                    logging.info(f"從文件 {city_file} 中讀取到 {len(city_data)} 項數據")
                    all_urls.extend(city_data)
            except Exception as e:
                logging.error(f"讀取城市文件 {city_file} 時發生錯誤: {e}")
        
        # 保存总文件
        logging.info(f"準備將所有城市數據合併保存到 {filename}")
        final_file = save_to_json(all_urls, filename)
        logging.info(f"已合併所有城市URL到總文件 {final_file}，共 {len(all_urls)} 個URL")
    
    logging.info("關閉WebDriver")
    driver.quit()
    logging.info(f"URL収集完成，共收集 {total_urls} 個URL")
    return temp_urls

# ------------------------------------------------
if __name__ == "__main__":
    log_file = setup_logging()
    logging.info(f"日誌檔案已建立：{log_file}")
    
    # 建立收集URL的資料夾
    os.makedirs('D:/allm/crawler/url_results', exist_ok=True)
    logging.info("已確保URL結果目錄存在")
    
    # 生成默认文件名用于整个过程
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_filename = f"search_urls_{timestamp}.json"
    logging.info(f"生成默認文件名: {default_filename}")
    
    # 收集URL
    logging.info("開始執行URL收集流程")
    collected_urls = collect_urls(filename=default_filename)
    
    logging.info("URL收集程式執行完畢") 