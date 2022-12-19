from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from os.path import exists
import csv
import time

url_csv_file = 'ContractorURLs-SmallBatch.csv'

export_csv_filename = 'ROC-Addresses.csv'

# for holding the resultant list
#element_list = []

page_list = []
address_list = []
#roc_addresses = {}

roc_addresses_test = {
    'https://azroc.my.site.com/AZRoc/s/contractor-search?licenseId=a0o8y000000NOP9AAO': '175 W Quail Springs Rd, Cottonwood, AZ, 86326',
    'https://azroc.my.site.com/AZRoc/s/contractor-search?licenseId=a0o8y0000004COZAA2': '175 W Quail Springs Rd, Cottonwood, AZ, 86327',
    'https://azroc.my.site.com/AZRoc/s/contractor-search?licenseId=a0ot0000000Ng23AAC': '175 W Quail Springs Rd, Cottonwood, AZ, 86328'
}

# Check if export csv exists. If so, get values already gone over so we can skip them and continue adding new addresses where it left off
page_black_list = []

if (exists(export_csv_filename)):
    print("Exported CSV found, will resume writing values.")
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

# I'm using chrome driver here instead of bs4 because I need to scrape dynamically generated html
def scrape_address(url): 
    with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as driver:
        driver.get(url)
        try:
            address_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="ServiceCommunityTemplate"]/div[2]/div/div/div/div/div[3]/div/div/div/div/div[2]/div[5]/div[1]/div/table/tr[2]/td/b/lightning-formatted-rich-text/span'))
            )
            address = address_element.find_elements(By.TAG_NAME, 'p')
            return address[0].text + ', ' + address[1].text
        except: 
            return "ERROR >>> Address Element Not Found"        

def test_scrape(p):
    return roc_addresses_test[p]

for page in page_list:
    #addr = scrape_address(page)
    addr = test_scrape(page)
    address_list.append(addr)

# Write new CSV file with page urls and addresses
with open(export_csv_filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for i in range(len(page_list)):
        writer.writerow([page_list[i], address_list[i]])

#print(roc_addresses.items())
