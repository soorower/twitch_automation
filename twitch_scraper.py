
from ssl import Options
from time import sleep
import pandas as pd
from bs4 import BeautifulSoup as bs
import sys
import gspread       
from oauth2client.service_account import ServiceAccountCredentials
import re
import os
import requests
sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),chrome_options=chrome_options)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
driver.maximize_window()



# game_url = f'https://www.twitch.tv/directory/game/Minecraft'
# game_url = 'https://m.twitch.tv/directory/game/VALORANT'
# game_url = str(input('Enter Game URL(ex. https://m.twitch.tv/directory/game/Minecraft): ')).replace('m.twitch','www.twitch')

def scrape():
    game_url = 'https://m.twitch.tv/directory/all'
    game_name = game_url.split('/')[-1].replace('%20',' ')
    driver.get(game_url)
    sleep(1)


    names = []
    count = 1
    profiles = []
    while True:
        print(f'scraping page: {count}')
        if count>600:
            break
        prev_len = len(profiles)
        count = count + 1
        try:
            element=driver.find_elements(By.XPATH,value =f"//div[@role='list']/div")[-1]
            element.location_once_scrolled_into_view
        except:
            element=driver.find_elements(By.XPATH, value=f"//div[@role='list']/div")[-1]
            element.location_once_scrolled_into_view
        sleep(1)
        soup = bs(driver.page_source,'html.parser')
        divs = soup.findAll('div',attrs= {'class':'Layout-sc-nxg1ff-0 kmugYy'})
        for div in divs:
            try:
                name = div.findAll('p')[1].text
                profiles.append(name)
                try:
                    tags = []
                    for tag in div.select('a[class*="ScTag-sc-xzp4i-0"]'):
                        tags.append(tag.text.strip())
                except:
                    tags = []
                if name in names:
                    tags = []
                else:
                    if 'English' in tags:
                        print(name)
                        print(tags)
                        names.append(name)
                    tags = []
            except:
                pass
        if len(profiles)== prev_len:
            sleep(5)
            print(f'scraping page: {count}..')
            prev_len = len(profiles)
            count = count + 1
            try:
                element=driver.find_elements(By.XPATH,value = f"//div[@role='list']/div")[-1]
                element.location_once_scrolled_into_view
            except:
                element=driver.find_elements_by_xpath(By.XPATH,value = f"//div[@role='list']/div")[-1]
                element.location_once_scrolled_into_view
            sleep(1)
            soup = bs(driver.page_source,'html.parser')
            divs = soup.find('div',attrs= {'role':'list'}).findAll('div')
            for div in divs:
                try:
                    name = div.findAll('p')[1].text
                    profiles.append(name)
                    try:
                        tags = []
                        for tag in div.select('a[class*="ScTag-sc-xzp4i-0"]'):
                            tags.append(tag.text.strip())
                    except:
                        tags = []
                    if name in names:
                        pass
                    else:
                        if 'English' in tags:
                            print(name)
                            print(tags)
                            names.append(name)
                except:
                    pass
            if len(profiles)== prev_len:
                print('No more profiles. So, scraping all profiles...')
                break



    #---------------------Each Profile Scrape about section------------------------------------

    headers = {
            'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
        }
    datan ={}
    listan = []
    print(f'Total Profiles Found: {len(names)}')
    count = 1
    for name in names:
        if '(' in name:
            pass
        else:
            url = f'https://m.twitch.tv/{name}/about'

            print(f'{count}. Scraping Profile: {name}; URL: {url}')
            count = count + 1
            r  = requests.get(url,headers = headers)
            soup = bs(r.content,'html.parser')

            try:
                real_emails = []
                mail_text = soup.find('p',attrs = {'class':'CoreText-sc-smutr2-0 cAvRQC'}).text.lower()
                emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", mail_text)
                
                for em in emails:
                    if '@' not in em:
                        pass
                    elif em in real_emails:
                        pass
                    elif 'png' in em or 'jpg' in em:
                        pass
                    elif '.' not in em:
                        pass
                    else:
                        real_emails.append(em)
                if len(real_emails) == 0:
                    if '@' in mail_text:
                        all_text_apart = mail_text.split(' ')
                        for each_text in all_text_apart:
                            if '@' in each_text:
                                if '.' in each_text:
                                    real_emails.append(each_text)
                            else:
                                pass
            except:
                real_emails = ''
            if len(real_emails)==0:
                real_emails = ''

            print(f'Emails Found: {real_emails}\n')
            if real_emails == '':
                pass
            else:
                datan = {
                    'Game Name': game_name,
                    'Profile URL': url,
                    'User Name': name,
                    'Email Address': real_emails[0],
                    'About Section': mail_text
                }
                listan.append(datan)
    df = pd.DataFrame(listan).drop_duplicates(subset=['Email Address'])
    df.to_excel(f'{game_name}_output.xlsx',encoding = 'utf-8-sig',index = False)

    # from google.colab import files
    # files.download(f'{game_name}_output.xlsx')


    #----------adding to sheet-----------------
    games = df['Game Name'].tolist()
    urls = df['Profile URL'].tolist()
    users = df['User Name'].tolist()
    emails = df['Email Address'].tolist()
    abouts = df['About Section'].tolist()

    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive.file']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    gc  = gspread.authorize(creds)

    try:
        sh = gc.open("Twitch CRM")
        try:
            worksheet = sh.worksheet("Twitch CRM")
        except:
            worksheet = sh.add_worksheet(title="Twitch CRM", rows=200000, cols=20)
        new_row_number = len(worksheet.col_values(1)) + 1
        
        worksheet2 = sh.worksheet("ff")
        banned_users = worksheet2.col_values(3)[1:]
        list_to_add = []
        emails_on_sheet = worksheet.col_values(4)
        for ga,ur,us,em,ab in zip(games,urls,users,emails,abouts):
            list_to = []
            if '.' not in em:
                pass
            elif em in emails_on_sheet:
                pass
            else:
                if us in banned_users:
                    pass
                else:
                    list_to.append(ga)
                    list_to.append(ur)
                    list_to.append(us)
                    list_to.append(em)
                    list_to.append(ab)
                    list_to_add.append(list_to)
        worksheet.update(f'A{new_row_number}:E150000', list_to_add)
    except:
        print('Wrong google sheet name. Your sheet name should be "Twitch CRM". If you want to change sheet name, let me know...')
    sleep(1500)


headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
}
while True:
    r = requests.get('https://www.timeanddate.com/worldclock/bangladesh/dhaka',headers= headers)
    soup = bs(r.content, 'html.parser')
    time1 = soup.find('span',attrs= {'id':'ct'}).get_text().lower()
    print(time1)
    time = time1[:5]
    
    if 'am' in str(time1):
        if '10:45' in str(time):
            scrape()
        if '10:46' in str(time):
            scrape()
        if '10:47' in str(time):
            scrape()
        if '10:48' in str(time):
            scrape()
        if '10:49' in str(time):
            scrape()
        if '10:50' in str(time):
            scrape()
        if '10:51' in str(time):
            scrape()
        if '10:52' in str(time):
            scrape()
        if '10:53' in str(time):
            scrape()
        if '1:19' in str(time):
            scrape()
        if '1:20' in str(time):
            scrape()
        if '1:21' in str(time):
            scrape()
        if '1:22' in str(time):
            scrape()
        if '1:23' in str(time):
            scrape()
    sleep(179)