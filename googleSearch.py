from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from getData import getAllPeopleSeperate, updateData
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def get_first_linkedin_result(driver, query):
    driver.get('https://www.google.com/')
    # print(driver.title)

    try:
        search = driver.find_element(By.NAME, 'q')
        print(search.tag_name)

        search.send_keys(query)
        search.send_keys(Keys.ENTER)

        first_item = driver.find_element(By.CLASS_NAME, "LC20lb")
        first_addr = driver.find_element(By.CLASS_NAME, "yuRUbf")

        addr = first_addr.find_element(By.TAG_NAME, 'a').get_attribute('href')
        print(f'{first_item.text} - {addr}')
        return f'{first_item.text} - {addr}'

    except NoSuchElementException:
        return None

    finally:
        # Clear the search box content after each search
        driver.find_element(By.NAME, 'q').clear()

def search():
    # chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    
    # #driver = webdriver.Chrome()
    # driver = webdriver.Chrome(options=chrome_options)

    # chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--disable-extensions")

    #driver = webdriver.Chrome(options=chrome_options)
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)

    try:
        people_list = getAllPeopleSeperate()
        for person in people_list:
            name = person['name']
            company = person['company']
            query = f'site:linkedin.com/in/ AND "{name}" AND "{company}"'
            result = get_first_linkedin_result(driver, query)
            if result is None:
                print('No result found')
                updateData(person['id'], "not found")
            else:
                print(f'Found: {result}')
                updateData(person['id'], result)  # Update data to Ragic
    finally:
        driver.quit()

if __name__ == "__main__":
    search()
