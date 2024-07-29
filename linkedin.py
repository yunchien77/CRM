from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from getData import getAllPeople, updateData
import logging
import pandas as pd
import os
import sys
import time
import getpass

def init_driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    return driver

def navigate_to_linkedin(driver):
    driver.get("https://www.linkedin.com/feed/")
    time.sleep(1)
    
def sign_in(driver):
    uname = driver.find_element(By.ID, "username")
    username = getpass.getpass("Enter your LinkedIn username: ")
    uname.send_keys(username)
    
    pword = driver.find_element(By.ID, "password")
    p = getpass.getpass("Enter your LinkedIn password: ")
    pword.send_keys(p)
    
    final_sign_in = driver.find_element(By.XPATH, '//*[@id="organic-div"]/form/div[3]/button')
    final_sign_in.click()
    
    driver.implicitly_wait(15)

def perform_person_search(driver, search_str):
    # 搜尋框
    #search_box = driver.find_element(By.CSS_SELECTOR, '#global-nav-typeahead > input')
    search_box = driver.find_element(By.CLASS_NAME, "search-global-typeahead__input")
    #<input class="search-global-typeahead__input" placeholder="Search" role="combobox" aria-autocomplete="list" aria-label="Search" aria-activedescendant="" aria-expanded="false" type="text">
    #search_box = driver.find_element(By.XPATH, "/html/body/div[6]/header/div/div/div/div[1]/input")
    #search_str = input("\nPlease specify the person's name that you are searching for: \n")
    search_box.send_keys(search_str)
    search_box.send_keys(Keys.ENTER)
    
    # 會員分類
    people_button = driver.find_element(By.CSS_SELECTOR, '#search-reusables__filters-bar > ul > li:nth-child(1) > button')
    #people_button = driver.find_element(By.XPATH, '/div/section/div/nav/div/ul/li[1]/div/button')
    people_button.click()

    search_box.clear()

def perform_person(driver, search_str):
    # 搜尋框
    search_box = driver.find_element(By.CLASS_NAME, "search-global-typeahead__input")
    search_box.send_keys(search_str)
    search_box.send_keys(Keys.ENTER)
    time.sleep(3)
    search_box.clear()

def scrape_people(driver):
    print('\n---> Person search begins....\n')

    # 檢查是否有 "No results found" 消息
    try:
        no_matching = driver.find_element(By.XPATH, "//h2[text()='No results found']")
        print(no_matching.text)
        return 'None', 'None'
    except NoSuchElementException:
        pass

    # 嘗試獲取搜索結果
    try:
        result = driver.find_element(By.CSS_SELECTOR, "li.reusable-search__result-container")
        
        try:
            #name_element = result.find_element(By.CSS_SELECTOR, "span.entity-result__title-text")
            name_element = result.find_element(By.CSS_SELECTOR, "span.entity-result__title-text a span[aria-hidden='true']")
            name = name_element.text.strip()
        except NoSuchElementException:
            name = "Name not available"

        # 嘗試獲取鏈接
        try:
            link_element = result.find_element(By.CSS_SELECTOR, "span.entity-result__title-text a")
            link = link_element.get_attribute('href')
        except NoSuchElementException:
            link = "Link not available"

        if name != 'Name not available' and link != 'Name not available':
            print(f"Name: {name}")
            print(f"Link: {link}")
            return name, link
        else:
            return 'None', 'None'

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return 'Error', 'Error'
    
def close_browser(driver):
    print(f'\nEnd Of Person Search!')
    driver.close()

def search():
    driver = init_driver()
    navigate_to_linkedin(driver)
    sign_in(driver)

    people_list = getAllPeople()
    count = 0

    for person in people_list:
        name = person['search']
        print(f'-----------{name}--------------')
        if count == 0:
            perform_person_search(driver, name)
        else: 
            perform_person(driver, person['search'])
        name, link = scrape_people(driver)
        
        if name != 'None' and link != 'None':
            updateData(person['id'], name + ' ' + link) #updata data to Ragic

        count += 1
        #time.sleep(1)
    
    close_browser(driver)

if __name__ == "__main__":
    search()