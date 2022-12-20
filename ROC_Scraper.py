from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os.path import exists
from fake_useragent import UserAgent
from tqdm import tqdm
import csv
import re
import time

url_csv_file = 'ContractorURLs-SmallBatch.csv'
export_csv_filename = 'ROC-Addresses.csv'

# For storing values that will be written to csv
page_list = []
address_list = []

# ChromeDriver options
options = Options()
options.headless = True
options.add_experimental_option('excludeSwitches', ['enable-logging'])

# Check if export csv exists. If so, get values already gone over so we can skip them and continue adding new addresses where it left off
page_black_list = []

if (exists(export_csv_filename)):
    tqdm.write("Exported CSV found, will resume writing values.")
    with open(export_csv_filename, 'r', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            page_black_list.append(row[0])
    
# Pull data from csv
with open(url_csv_file, 'r', newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        # Check if item is in black list before appending
        if row[0] not in page_black_list:
            page_list.append(row[0])

regex_err_ct = 0

def regex_search(html):
    global regex_err_ct
    regex_find_addr = "\d{2,5} .+ \d{5}"
    regex_find_po = "(PO|P\.O\.)+(\w|\d|\s){1,5}\d{2,5}.+\d{5}"
    # Remove Returns / Newlines
    html_string = html.replace('\n', ' ')
    # Search for address
    str_address = re.search(regex_find_addr, html_string, flags=re.I)
    # Search for PO Box
    po_box = re.search(regex_find_po, html_string, flags=re.I)

    if str_address:
        return str_address.group()
    elif po_box:
        return po_box.group()
    else:
        regex_err_ct += 1
        tqdm.write('RegEx Error: Unable to get address from this string: ' + html_string)
        return 'ERROR >>> RegEx unable to get address. ' + html_string

el_locator_err_ct = 0

# I'm using chrome driver here instead of bs4 because I need to scrape dynamically generated html
def scrape_address(url): 
    global el_locator_err_ct
    user_agent = UserAgent().random
    options.add_argument(f'user-agent={user_agent}')
    with webdriver.Chrome(options=options) as driver:
        driver.get(url)
        #tqdm.write('UA: ' + user_agent)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'table.slds-table'))
            )
        except: 
            el_locator_err_ct += 1
            tqdm.write('Location Error: Address element not found on this page: ' + url)
            mailing_address = 'ERROR >>> Address Element Not Found'
        else:
            time.sleep(1)
            table = driver.find_element(By.CSS_SELECTOR, 'table.slds-table')
            #table_txt = address_container
            mailing_address = regex_search(table.text)
        finally:
            return mailing_address   

for page in tqdm(page_list, desc='Progress: '):
    addr = scrape_address(page)
    address_list.append(addr)

# Write new CSV file with page urls and addresses
with open(export_csv_filename, 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for i in range(len(page_list)):
        writer.writerow([page_list[i], address_list[i]])

print('Process complete. \n' + str(regex_err_ct) + ' RegEx Errors. \n' + str(el_locator_err_ct) + ' Element Locator Errors.')