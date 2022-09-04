from time import sleep
import pandas as pd
from bs4 import BeautifulSoup as bs
import sys
import gspread       
from oauth2client.service_account import ServiceAccountCredentials
import re
import requests
sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')
from selenium import webdriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
# driver = webdriver.Chrome('chromedriver',options=chrome_options)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


import chromedriver_autoinstaller
chromedriver_autoinstaller.install()
driver = webdriver.Chrome()

driver.maximize_window()



# game_url = f'https://www.twitch.tv/directory/game/Minecraft'
# game_url = 'https://m.twitch.tv/directory/game/VALORANT'
# game_url = str(input('Enter Game URL(ex. https://m.twitch.tv/directory/game/Minecraft): ')).replace('m.twitch','www.twitch')

game_url = 'https://www.twitch.tv/directory/all/tags/English'

game_name = game_url.split('/')[-1].replace('%20',' ')
driver.get(game_url)
sleep(1)
element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search Tags']"))
    )

names = []
count = 1
num  = 20
while True:
    sleep(1)
    print(f'Scrolling number: {count}')
    prev_len = len(names)
    count = count + 1
    if count == 5000:
        break
    try:
        try:
            element=driver.find_element(By.XPATH, value = f"//div[@class='ScTower-sc-1dei8tr-0 dcmlaV tw-tower']/div[{num}]")
            
            element.location_once_scrolled_into_view
            num = num + 20
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//div[@class='ScTower-sc-1dei8tr-0 dcmlaV tw-tower']/div[{num}]"))
            )
        except:
            num = num - 10
            element=driver.find_element(By.XPATH, value = f"//div[@class='ScTower-sc-1dei8tr-0 dcmlaV tw-tower']/div[{num}]")
            
            element.location_once_scrolled_into_view
            num = num + 30
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//div[@class='ScTower-sc-1dei8tr-0 dcmlaV tw-tower']/div[{num}]"))
            )
    except:
        print('break')
        break
   
    soup = bs(driver.page_source,'html.parser')
    main_divs = soup.findAll('p',attrs = {'class':'CoreText-sc-cpl358-0 eyuUlK'})
    for div in main_divs:
        try:
            name = div.text.strip()
            if name in names:
                pass
            else:
                names.append(name)
        except:
            pass
    if len(names) == prev_len:
        sleep(4)
        print(f'Scrolling number: {count}.')
        prev_len = len(names)
        count = count + 1
        if count == 5000:
            break
        try:
            try:
                element=driver.find_element(By.XPATH, value = f"//div[@class='ScTower-sc-1dei8tr-0 dcmlaV tw-tower']/div[{num}]")
                
                element.location_once_scrolled_into_view
                num = num + 20
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//div[@class='ScTower-sc-1dei8tr-0 dcmlaV tw-tower']/div[{num}]"))
                )
            except:
                num = num - 10
                element=driver.find_element(By.XPATH, value = f"//div[@class='ScTower-sc-1dei8tr-0 dcmlaV tw-tower']/div[{num}]")
                
                element.location_once_scrolled_into_view
                num = num + 30
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//div[@class='ScTower-sc-1dei8tr-0 dcmlaV tw-tower']/div[{num}]"))
                )
        except:
            print('break')
            break
    
        soup = bs(driver.page_source,'html.parser')
        main_divs = soup.findAll('p',attrs = {'class':'CoreText-sc-cpl358-0 eyuUlK'})
        for div in main_divs:
            try:
                name = div.text.strip()
                if name in names:
                    pass
                else:
                    names.append(name)
            except:
                pass
        if len(names) == prev_len:
            print('No more profile URL found. Scraping Each Profle Started...\n')
            break
    # print(len(names))


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

    list_to_add = []
    emails_on_sheet = worksheet.col_values(4)
    for ga,ur,us,em,ab in zip(games,urls,users,emails,abouts):
        list_to = []
        if '.' not in em:
            pass
        elif em in emails_on_sheet:
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