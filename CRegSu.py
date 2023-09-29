
    
##ver 1 old

import requests
from bs4 import BeautifulSoup
import time
import hashlib

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

LOGIN_URL = 'https://suis.sabanciuniv.edu/prod/twbkwbis.P_SabanciLogin'
SUB_LINK_AFTER_LOGIN = 'https://suis.sabanciuniv.edu/prod/bwskfreg.P_AltPin'
USERNAME = 'tolgabasak'
PASSWORD = 'Tb_843749'

BASE_URL = 'https://suis.sabanciuniv.edu/prod/bwckschd.p_disp_detail_sched?term_in=202301&crn_in='
CRN_LIST = ['10135', '10147', '10172', '10173', '10175', '10180']

INTERVAL = 0.005 # 0.5 sec

#10150 - CS 308  x
#12026 - CS 308L x
#10135 - CS 307
#10147 - CS 307R
#10172 - CS 405
#10173 - CS 405L
#10175 - CS 408
#10180 - CS 408L
#10636 - NS 206 aldım

def get_website_content(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def login_and_navigate(changed_crn):
    driver = webdriver.Chrome()
    driver.get(LOGIN_URL)

    # Login
    username_elem = driver.find_element_by_name('sid')
    password_elem = driver.find_element_by_name('PIN')
    username_elem.send_keys(USERNAME)
    password_elem.send_keys(PASSWORD)
    password_elem.send_keys(Keys.RETURN)

    time.sleep(1)

    # to the sublink
    driver.get(SUB_LINK_AFTER_LOGIN)

    # CRN 10150 changed, drop CS411-5th course-action_id5
    if changed_crn == '10150':
        course_drop_selection = driver.find_element_by_id('action_id5')
        for option in course_drop_selection.find_elements_by_tag_name('option'):
            if option.text == 'Web Drop Course':
                option.click()
                break

    # Input CRN list
    for idx, crn in enumerate(CRN_LIST, start=1):
        crn_input = driver.find_element_by_id(f'crn_id{idx}')
        crn_input.send_keys(crn)

    # "Submit Changes"
    submit_button = driver.find_element_by_xpath('//input[@name="REG_BTN" and @value="Submit Changes"]')
    print(f"Got CRN {changed_crn}!")
    submit_button.click()


def main():
    old_hashes = {crn: None for crn in CRN_LIST}
    
    while True:
        for crn in CRN_LIST:
            print(f"Running CRN {crn}...")
            
            url = BASE_URL + crn
            content = get_website_content(url)
            soup = BeautifulSoup(content, 'html.parser')
            
            td_tags = soup.find_all('td', {'class': 'dddefault'})
            target_td = next((td for td in td_tags if td.text.strip() == "0"), None)
            
            if not target_td:
                print(f"not found for CRN {crn}!")
            else:
                data = target_td.text.strip()
                new_hash = hashlib.md5(data.encode('utf-8')).hexdigest()
                
                if old_hashes[crn] and old_hashes[crn] != new_hash:
                    print(f"CRN {crn} has changed!")
                    login_and_navigate(crn)  # Call this function upon change detection and pass the CRN
                
                old_hashes[crn] = new_hash
            
            time.sleep(INTERVAL)

if __name__ == '__main__':
    main()
    
    
