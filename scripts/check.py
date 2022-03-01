import tkinter
import random
import time
import os

from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from .types import StartEvent
from . import utils


LOGIN_URL = 'https://twitter.com/i/flow/login'
URL_HOME = 'https://twitter.com/home'


options = Options()
options.add_argument('headless')
options.add_argument('window-size=1920x935')

if os.name == 'nt':
    service = Service(os.path.join(os.getcwd(), 'static', 'chromedriver_nt.exe'))
else:
    service = Service(os.path.join(os.getcwd(), 'static', 'chromedriver_mac'))


class TwoFactor(Exception):
    pass

class InvalidPassword(Exception):
    pass


def _login(driver: webdriver.Chrome, wait: WebDriverWait, user: str, password: str) -> None:
    driver.get(LOGIN_URL)

    wait.until(ec.element_to_be_clickable((By.XPATH, '//input[@name="text"]')))
    time.sleep(3)

    driver.find_element(By.XPATH, '//input[@name="text"]').send_keys(user, Keys.ENTER)
    time.sleep(2)

    driver.find_element(By.XPATH, '//input[@name="password"]').send_keys(password, Keys.ENTER)
    time.sleep(3)


    if driver.current_url == LOGIN_URL:
        try:
            element = driver.find_element(By.CLASS_NAME, 'css-1dbjc4n.r-mk0yit.r-1f1sjgu')
            element.find_element(By.NAME, 'text')
        except NoSuchElementException:
            raise InvalidPassword
        else:
            raise TwoFactor


def _grab_data(driver: webdriver.Chrome) -> tuple:
    panel = driver.find_element(By.XPATH, '//nav[@role="navigation"]')
    panel.find_element(By.XPATH, '//a[@data-testid="AppTabBar_Profile_Link"]').click()
    time.sleep(3)

    info_panel = driver.find_element(By.CLASS_NAME, 'css-1dbjc4n.r-1ifxtd0.r-ymttw5.r-ttdzmv')

    tweet = driver.find_element(By.CLASS_NAME, 'css-901oao.css-bfa6kz.r-14j79pv.r-37j5jr')
    num_tweets = tweet.text.split(' ')[0]

    reg_div = info_panel.find_element(By.XPATH, '//div[@data-testid="UserProfileHeader_Items"]')
    create_at = reg_div.text.split(' ', 1)[1]

    element = info_panel.find_element(By.CLASS_NAME, 'css-1dbjc4n.r-13awgt0.r-18u37iz')
    followers = element.find_element(By.XPATH, '//div[@class="css-1dbjc4n"]/a')
    num_followers = followers.text.split(' ')[0]

    return create_at, num_followers, num_tweets


def checking(self, event: StartEvent) -> None:
    account_path = event.files_path.get('account-path')
    proxy_path = event.files_path.get('proxy-path', '')
    logger = event.logger

    users, actions = [], 0

    raw = utils.file_parser(proxy_path)
    options.add_argument(f'--proxy-server={utils.get_proxy(raw)}')

    try:
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 20)
    except WebDriverException:
        return logger.update('An error occurred while creating webdriver.')

    logger.update('Starting process!')


    for user, password in utils.file_parser(account_path):
        try:
            _login(driver, wait, user, password)
        except NoSuchElementException:
            logger.update(f'An unknown error occurred while logging into {user}')
        except TwoFactor:
            logger.update(f'{user} - Authorization Error: Two-Factor authentication.')
            utils.write_account('2fa', user, password)
        except InvalidPassword:
            logger.update(f'{user} - Authorization Error: Wrong password.')
            utils.write_account('badpass', user, password)

        if driver.current_url != URL_HOME:
            continue

        logger.update(f'{user} - Successful login.')
        users.append((user, *_grab_data(driver)))

        if actions >= event.action:
            break

        time.sleep(random.randint(0, event.time))
        actions += 1

    logger.update('Process completed.')
    utils.write_data(users)
    driver.quit()

    self.button_start.config(state=tkinter.NORMAL)
    self.button_1.config(state=tkinter.NORMAL)
    self.button_2.config(state=tkinter.NORMAL)
    self.button_3.config(state=tkinter.NORMAL)

    self.entry_1.config(state=tkinter.NORMAL)
    self.entry_2.config(state=tkinter.NORMAL)

    self.checkbox_1.config(state=tkinter.NORMAL)
    self.checkbox_2.config(state=tkinter.NORMAL)
    self.checkbox_3.config(state=tkinter.NORMAL)
    self.checkbox_4.config(state=tkinter.NORMAL)
