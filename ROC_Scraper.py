from bs4 import BeautifulSoup
import requests
import csv

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

# r = requests.get(searchURL, headers=headers)

# print(r)

csv_file = 'ContractorURLs-SmallBatch.csv'

def scrape_page(p):
    r = requests.get(p, headers=headers)
    if (r.status_code != 200):
        print('Error ' + r.status_code + ' ' + p)
        return
    soup = BeautifulSoup(r.text, 'html.parser')
    heading = soup.find('h1')
    print(heading)
    # table = soup.find('table', class_='slds-table')
    # if table == None:
    #     print('Tag not found here: ' + p)
    #     return
    # address = table.find('tr'[2]).decendants.find('span')
    # print(address.strings)

with open(csv_file, 'r', newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        scrape_page(row[0])

