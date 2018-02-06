import glob
import pickle
import threading


import transcript
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium import webdriver
import os
import config
from selenium.common.exceptions import NoSuchElementException

import logging
import telegram_bot


logging.basicConfig(format='%(asctime)s - %(name)12s - %(levelname)s - %(message)s',
                    level=logging.INFO)
# logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
#                     level=logging.INFO)
logger = logging.getLogger(__name__)

driver = None
wait = None
COOKIES_FILE_NAME = 'cookies.pkl'
old_transcript_md5 = None


def enable_download_in_headless_chrome(driver, download_dir):
    # add missing support for chrome "send_command"  to selenium webdriver
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    command_result = driver.execute("send_command", params)


def web_driver_setup():
    logger.info('Do web driver setup...')
    global driver
    global wait
    chrome_options = webdriver.ChromeOptions()
    download_dir = os.path.dirname(os.path.abspath(__file__))
    prefs = {"download.default_directory": download_dir}
    chrome_options.add_experimental_option("prefs", prefs)

    if config.headless:
        chrome_options.add_argument('headless')

    driver = webdriver.Chrome(chrome_options=chrome_options)

    if config.headless:
        enable_download_in_headless_chrome(driver, download_dir)

    # driver.implicitly_wait(30)
    wait = WebDriverWait(driver, 10)


def check_exists_by_xpath(xpath):
    # driver.implicitly_wait(0)
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    finally:
        pass
        # driver.implicitly_wait(30)
    return True


def check_exists_by_id(id):
    # driver.implicitly_wait(0)
    try:
        driver.find_element_by_id(id)
    except NoSuchElementException:
        return False
    finally:
        pass
        # driver.implicitly_wait(30)
    return True


def login():
    url = "https://swsdownload.vtc.edu.hk/swsdownload/"
    driver.get(url)
    if os.path.exists(COOKIES_FILE_NAME):
        cookies = pickle.load(open(COOKIES_FILE_NAME, "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.get(url)

    logger.info('Check auth...')
    if check_exists_by_xpath('//*[@data-loginstatus="login"]'):
        logger.info('Do login...')
        driver.find_element_by_id("nav_login_btn").click()
        input_id = 'inputuid'
        wait.until(EC.visibility_of_element_located((By.ID, input_id)))
        driver.find_element_by_id(input_id).clear()
        driver.find_element_by_id(input_id).send_keys(config.student_id)
        input_id = 'in_pwd'
        driver.find_element_by_name(input_id).clear()
        driver.find_element_by_name(input_id).send_keys(config.password)
        driver.find_element_by_css_selector("button.modal_box_btn.primary").click()
    else:
        logger.info('Already login')


def download_transcript():
    logger.info('Do download_transcript...')
    wait.until(EC.visibility_of_element_located((By.ID, "transcript")))
    pickle.dump(driver.get_cookies(), open(COOKIES_FILE_NAME, "wb"))
    driver.find_element_by_css_selector("img.download_item_icon_img").click()
    css_selector = 'a.modal_box_btn.fileDownloadBtn.primary'
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
    driver.find_element_by_css_selector(css_selector).click()


def init():
    global old_transcript_md5

    if glob.glob("*.pdf"):
        logger.error('Please delete all pdf file first! (except the pdf under old_transcript)')
        exit()
    if config.start_bot:
        telegram_bot.main()

    old_transcript_md5 = transcript.get_old_transcript_md5()
    web_driver_setup()


def main():
    global old_transcript_md5

    try:
        login()
        download_transcript()
    except Exception as error:
        logger.error(str(error))

    # wait for download complete
    while not transcript.check_for_files("*.pdf"):
        time.sleep(1)

    file_name = glob.glob("*.pdf")[0]  # get the transcript file name

    # if old transcript in old_transcript folder
    if old_transcript_md5:
        if transcript.is_different_transcript(old_transcript_md5):
            telegram_bot.send_message_async(file_name)
            os.startfile(file_name)
            logger.info('Transcript released!')
            driver.quit()
        else:
            threading.Timer(config.interval, main).start()
            logger.info('-' * 50)
            logger.info('Wait ' + str(config.interval / 60) + ' minute...')
    else:
        logger.info('Moving the transcript to old_transcript folder...')
        logger.info('-' * 50)
        path = os.path.dirname(os.path.abspath(__file__)) + '\\'
        moveto = path + '\\old_transcript\\'
        os.rename(path + file_name, moveto + file_name)
        old_transcript_md5 = transcript.get_old_transcript_md5()
        main()


if __name__ == "__main__":
    init()
    main()
