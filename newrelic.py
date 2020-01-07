from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import date, timedelta
import pygsheets
import time
import string
from settings import api_url, api_sheet, api_overview, api_performance, api_endpoints, api_transaction_endpoints
from settings import web_url, web_sheet, web_overview, web_performance, web_endpoints, web_transaction_endpoints

today = date.today() #- timedelta(days=1)

dat = today.strftime("%d-%B-%Y")

alpha = (list(string.ascii_uppercase)[1:13])
def newrelic_data (url,sheet,overview,performance,endpoints,gsheet_endpoints):
    options = Options()
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    #options.add_argument("--start-maximized")
    #options.add_argument('window-size=1500,1000')
    #options.add_argument("--start-maximized")

    driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver', options=options)
    driver.get(url)
    
    Email = driver.find_element_by_id('login_email').send_keys('xxxx')
    Passwd= driver.find_element_by_id('login_password').send_keys('zzzzzzzzzxxxxxxxxxx')
    login= driver.find_element_by_id('login_submit').click()

#last 6 hrs

    WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="time_window_nav"]/h4')))
    driver.find_element_by_xpath('//*[@id="time_window_nav"]/h4').click()
    WebDriverWait(driver,30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="time_window_ranges"]/li[4]/a/span')))
    #time.sleep(5)
    driver.find_element_by_xpath('//*[@id="time_window_ranges"]/li[4]/a/span').click()
    time.sleep(5)

#max throughput

    users = driver.execute_script("return Highcharts.charts[0].series[0].yData");

    max_throughput= max(users)

#==================================================

    endpoint_values=[]
    for i in range(1,21):
        a = driver.find_element_by_xpath('//*[@id="bar_chart_list_by_time_consumed_filtered_"]/ol/li[{}]/a'.format(i))
        items = a.find_elements_by_tag_name("span")
        for item in items:
            b = item.text
            endpoint_values.append(b)
    
    end_point=[]
    html_list = driver.find_element_by_xpath('//*[@id="bar_chart_list_by_time_consumed_filtered_"]/ol')
    items2 = html_list.find_elements_by_tag_name("p")

    for item in items2:
        text = item.text
        end_point.append(text)
    keys=(list(filter(None, end_point)))

    dictionary=dict(zip(keys, endpoint_values))
    
    #sample_endpoints= gsheet_endpoints 
    #sample_values = []
    #for i in sample_endpoints:
     #   for k in dictionary.keys():
      #      if i == k:
       #         sample_values.append(dictionary[k])
        #        break
    #final = dict(zip(alpha,sample_values))



#Overview

    ms = []
    #overview.click()
    if url == api_url:
        driver.get(overview)
    else:
        driver.get(overview)
    time.sleep(10)
    driver.find_element_by_xpath('//*[@id="time_window_nav"]/h4').click()
    time.sleep(10)
    driver.find_element_by_xpath('//*[@id="time_window_ranges"]/li[4]/a/span').click()
    time.sleep(10)
    #screen_short = driver.save_screenshot("/home/praveen/newrelic.png")
    response = driver.find_element_by_xpath('//*[@id="app_response"]/h2') 

    response_time = response.find_elements_by_tag_name("p")
    for i in response_time:
        text = i.text
        ms.append(text)
    avg_resp_time = (list(filter(None, ms)))

    driver.close()

#gsheet
    credentials = pygsheets.authorize(service_file='/root/NewRelic-6d54dec5d48c.json')
    sheet = credentials.open_by_url(sheet)
    
    ws1 = sheet.worksheet('title',performance)
    for i in range(2,10000):
        if ws1.get_value('A{}'.format(i)) == "":
            next_row = i
            break
        #ws1 = sheet.worksheet('title',performance)
    ws1.update_value('A{}'.format(next_row),dat)
    ws1.update_value('B{}'.format(next_row),max_throughput)
    if url == web_url:
        ws1.update_value('C{}'.format(next_row),avg_resp_time[2])
    else:
        ws1.update_value('C{}'.format(next_row),avg_resp_time[0])
    ws1_bor=pygsheets.DataRange(start='A{}'.format(next_row), end='C{}'.format(next_row), worksheet=ws1).update_borders(top=True, right=True, bottom=True, left=True, inner_horizontal=True,inner_vertical=True,style='SOLID')
    #elif:
    ws2 = sheet.worksheet('title',endpoints)
    for i in range(3,10000):
        if ws2.get_value('A{}'.format(i)) == "":
            ws2_next_row = i
            break
    ws2.update_value('A{}'.format(ws2_next_row),dat)
    #for x,y in final.items():
        #ws2.update_value('{}{}'.format(x,ws2_next_row),y)
    for i in alpha:
        value = ws2.get_value('{}2'.format(i))
        #n =+ 1
        if value in list(dictionary.keys()):
            ws2.update_value('{}{}'.format(i,ws2_next_row),dictionary[value])
        else:
            ws2.update_value('{}{}'.format(i,ws2_next_row),"----")

    ws2_bor=pygsheets.DataRange(start='A{}'.format(ws2_next_row), end='M{}'.format(ws2_next_row), worksheet=ws2).update_borders(top=True, right=True, bottom=True, left=True, inner_horizontal=True,inner_vertical=True,style='SOLID')

update_api_sheet = newrelic_data(api_url,api_sheet,api_overview,api_performance,api_endpoints,api_transaction_endpoints)
print('API Completed Successfully....')
update_web_sheet = newrelic_data(web_url,web_sheet,web_overview,web_performance,web_endpoints,web_transaction_endpoints)
print('WebApp Completed Successfully.....')

