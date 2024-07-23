from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
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

def perform_person_search(driver):
    # 搜尋框
    search_box = driver.find_element(By.CSS_SELECTOR, '#global-nav-typeahead > input')
    person_name = input("\nPlease specify the person's name that you are searching for: \n")

    search_box.send_keys(person_name)
    search_box.send_keys(Keys.ENTER)
    
    # 會員分類
    people_button = driver.find_element(By.CSS_SELECTOR, '#search-reusables__filters-bar > ul > li:nth-child(1) > button')
    people_button.click()
    return person_name

def scrape_people(driver):
    try:
        #no_matching_people = driver.find_element(By.XPATH, "/html/body/div[6]/div[3]/div[2]/div/div[1]/main/div/div/div/section/h2")
        #print(no_matching_people.text)
        #print('\nNo matching people found.')

        no_matching = driver.find_element(By.XPATH, "//h2[text()='No results found']")
        print(no_matching.text)
        
    except NoSuchElementException:
        print('\n---> Person search begins....\n')
        
        result = driver.find_element(By.CSS_SELECTOR, "li.reusable-search__result-container")
        
        name_element = result.find_element(By.CSS_SELECTOR, "span.entity-result__title-text a span[aria-hidden='true']")
        link_element = result.find_element(By.CSS_SELECTOR, "span.entity-result__title-text a")
        
        name = name_element.text
        link = link_element.get_attribute('href')
        
        print(f"Name: {name}")
        print(f"Link: {link}")
    
def close_browser(driver):
    print(f'\nEnd Of Person Search!')
    driver.close()

if __name__ == "__main__":
    driver = init_driver()
    navigate_to_linkedin(driver)
    sign_in(driver)
    person_name = perform_person_search(driver)
    information = scrape_people(driver)
    close_browser(driver)
