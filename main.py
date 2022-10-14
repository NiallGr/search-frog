from datetime import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
import requests
import time

Category_started = 0
# Headers for the CSV file
columnslist = ["Source", "Firm", "Address Line 1", "Telephone Number", "URL"]
alldata = []
empty = pd.DataFrame(alldata, columns=columnslist)
empty.to_csv('searchFrogCom.csv', encoding='utf-8-sig', index=False)


def html_clean(in_tuple):
    # cleanup html to text and remove unneeded characters
    list = []
    for element in in_tuple:
        if element is None:
            list.append("null")
        else:
            # print(element)
            if type(element) is str:
                list.append(element.strip().replace(" ", "").replace("\n", "").replace("\r", "").replace("mailto:", ""))
            else:
                # print(element)
                object = element.text.strip()

                object = object.replace("\n", "").replace("\r", "").replace("mailto:", "")
                # object = element.text.strip.replace(" " , " ").replace("\n", "").replace("\r", "")#
                list.append(object)

    return (tuple(list))


def link_fetch():
    souplist = []
    current_page_turned_to_soup = 0
    for i in range(1, 532, 1):


        headers = {
            'authority': 'searchfrog.com.au',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            # Requests sorts cookies= alphabetically
            # 'cookie': '_gid=GA1.3.389627547.1665408411; _gat_gtag_UA_100092030_1=1; _ga=GA1.1.280120100.1665158594; _ga_BYFT999XDT=GS1.1.1665415354.3.1.1665415367.0.0.0',
            'origin': 'https://searchfrog.com.au',
            'referer': 'https://searchfrog.com.au/?select=&lp_s_loc=17&lp_s_tag=&lp_s_cat=&s=home&post_type=listing',
            'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        data = {
            'action': 'ajax_search_tags',
            'cat_id': '',
            'loc_id': '17',
            'list_style': '',
            'pageno': f'{i}',
            'skeyword': '',
            'clat': '',
            'clong': '',
            'my_bounds_ne_lat': '',
            'my_bounds_ne_lng': '',
            'my_bounds_sw_lat': '',
            'my_bounds_sw_lng': '',
            'data_zoom': '',
            'distance_range': '105',
            'lpNonce': '3084fc9daa',
        }

        response = requests.post('https://searchfrog.com.au/wp-admin/admin-ajax.php', headers=headers, data=data).json()

        html = response['html']
        #
        soup = BeautifulSoup(html, 'lxml')
        time.sleep(2)
        current_page_turned_to_soup += 1
        print(f"Pages turned to soup object {current_page_turned_to_soup}")
        souplist.append(soup)
    return souplist


def scrape(soup):

    sections_containing_link = soup.find_all("div", "show-img")

    # print(sections_containing_link)
    results_completed = 0
    list_of_data = []
    for sections_links in sections_containing_link:
        links_anchor = sections_links.find("a")
        links_href = links_anchor.get("href")

        result_2 = requests.get(links_href).text
        # print(urls)
        soup_2 = BeautifulSoup(result_2, 'lxml')
        # Source
        Source = "https://searchfrog.com.au/?select=&lp_s_loc=17&lp_s_tag=&lp_s_cat=&s=home&post_type=listing"
        # Firm
        try:
            firm = soup_2.find_all("h1")[0]
        except:
            firm = "Null"
        # Address
        try:
            address = soup_2.select_one("ul > li.lp-details-address > a > span:nth-child(2)").text.strip()
        except:
            address = "Null"
        # Telephone Number
        try:
            telephone = soup_2.select_one("ul > li.lp-listing-phone > a").text.strip()
        except:
            telephone = "Null"
        # URL
        try:
            URL = soup_2.select_one("ul > li.lp-user-web > a > span:nth-child(2)").text.strip()
        except:
            URL = "Null"

        list_of_data.append((Source, firm, address, telephone, URL))
        results_completed += 1
    return list_of_data

souplist = link_fetch()

for soup in souplist:
    datalist = scrape(soup)
    for data in datalist:
        try:
            data = html_clean(data)
            alldata.append(data)
            df = pd.DataFrame([data], columns=columnslist)
            df.to_csv('searchFrogCom.csv', encoding='utf-8-sig', index=False, mode='a', header=False)
            time.sleep(0.1)
            print("Saved with a total volume of: ", len(alldata))
        except Exception as e:
            print('Scrape ended early, refer to error message, saving scraped data to file')
            print(e)
            df = pd.DataFrame(alldata, columns=columnslist)
            df.to_csv('searchFrogCom_crashed.csv', encoding='utf-8-sig', index=False)
            print("Saved with a total volume of: ", len(df))



