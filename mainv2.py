# -*- coding: utf-8 -*-
import time
import os
import sys
import urllib
import urllib.request


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import Select
import requests
from PIL import Image
from twocaptcha import TwoCaptcha



API = input('Вставьте ключ rucaptcha: ')

#API = '85a9a133c454bea489b63692901579b6'

class SendReport():
    def __init__(self):
        chrome_options = Options()
        #chrome_options.add_argument("--window-size=499,800")
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument("--start-maximized")
        self.url = 'https://eais.rkn.gov.ru/feedback/'
        self.driver = webdriver.Chrome(options=chrome_options,
                                       executable_path=os.getcwd() + './chromedriver')
        
    def captcha_response(self, captcha_api_key):
        api_key = os.getenv('APIKEY_2CAPTCHA', f'{captcha_api_key}')
        solver = TwoCaptcha(api_key)
        result = solver.normal('current_captcha.png')
        return result['code']

    def crop_default(self):
        self.driver.save_screenshot("fullPageScreenshot.png")
        left = 1035
        top = 850
        fullImg = Image.open("fullPageScreenshot.png")
        width = 205
        height = 65
        cropImg = fullImg.crop((left, top, left + width, top + height))
        cropImg.save("current_captcha.png")
        
    def main(self):
        url_list = []
        #  читаем ссылки из файла
        url_file = open('url.txt')
        for i in url_file:
            url_list.append(i.replace('\n',''))
        url_file.close()
        try_count = 0
        for i in url_list:
            self.driver.get(self.url)
            select = Select(self.driver.find_element_by_id('Type'))
            select.select_by_visible_text('азартные игры')  # тип жалобы
            self.driver.find_element_by_id("ResourceUrl").send_keys(i)  # адрес ресурса
            self.driver.find_element_by_id("screenShot").send_keys(os.getcwd() + './1.jpeg')  #  Вложение
            self.driver.find_element_by_xpath("//input[contains(@value,'32')]").click()  #  рисованные изображения
            self.driver.find_element_by_xpath("//input[@value='2']").click()  #  фото изображения
            self.driver.find_element_by_xpath("//input[@value='4']").click()  #  текст
            self.driver.find_element_by_xpath("//input[contains(@value,'64')]").click()  #  анимационное изображение
            self.driver.find_element_by_xpath("//input[@value='16']").click()  #  Другое
            self.driver.find_element_by_xpath("//textarea[@class='inputTxt']").send_keys('Сайт онлайн казино')  # доп. инфа
        
            
            self.driver.find_element_by_id("captcha_image").click()
            self.crop_default() #  фоткаем капчу
            
            while True:
                captcha_solve_data = self.captcha_response(API)  # щлём капчу на разгадку
                captcha_field = self.driver.find_element_by_xpath("//input[@id='captcha']")
                captcha_field.send_keys(captcha_solve_data)  #  вводим капчу
                captcha_field.send_keys(Keys.TAB)
                time.sleep(1)
                action = ActionChains(self.driver)
                action.send_keys(Keys.ENTER)
                action.perform()
                time.sleep(5)
                if 'Неверно указан защитный код' in self.driver.page_source:
                    try_count += 1
                    self.driver.find_element_by_xpath("//button[contains(.,'Закрыть')]").click()
                    """time.sleep(2)"""
                    # clear cap field
                    cap_field = self.driver.find_element_by_xpath("//input[@id='captcha']")
                    for k in range(1,15):
                        cap_field.send_keys(Keys.BACK_SPACE)
                    continue
                    
                elif 'Число обращений с одного адреса превысило допустимое. Повторите отправку позже.2' in self.driver.page_source:
                    time.sleep(5)
                    action2 = ActionChains(self.driver)
                    action2.send_keys(Keys.ENTER)
                    action2.perform()
                    
                    time.sleep(3)
                    if 'Ваше сообщение отправлено. Спасибо' in self.driver.page_source:
                        print('Отправили жалобу на сайт:', i)
                        try_count = 0
                        # Пишем зареганнйы аккаунт в файл, для отчёта
                        log_file = open('already_send.txt', 'a')
                        log_file.write(f'{i}' + '\n')
                        log_file.close()
                        break
            
                elif 'Ваше сообщение отправлено. Спасибо' in self.driver.page_source:
                    print('Отправили жалобу на сайт:', i)
                    try_count = 0
                    # Пишем зареганнйы аккаунт в файл, для отчёта
                    log_file = open('already_send.txt', 'a')
                    log_file.write(f'{i}' + '\n')
                    log_file.close()
                    break
            if try_count > 5:
                continue
        self.driver.close()
        print('Успешно завершили отправку.')
        
        
if __name__ == '__main__':
    browser = SendReport()
    browser.main()