'''
Samir Townsley
March 3, 2020
NCAA Tournament Data Scraper

Source: www.sports-reference.com
'''


#### Usage ##########################
#
# Run with default parameters:
#       python3 get_tourney_data.py
#
# Run with manual parameter entry:
#       python3 get_tourney_data.py 1
#
#####################################


from bs4 import BeautifulSoup as bs
import pandas as pd
import unicodedata
import requests
import csv
import sys

### Set year parameters
if len(sys.argv) == 1:  # Default year range
    start = 1987    # Introduction of 3-pt line and shot clock
    end = 2019
else:   # Manual year entry
    if sys.argv[1] == '1':
        start = input('Enter start year: ')
        end = input('Enter end year: ')
    else:
        print('Error: Invalid argument \'%s\'' % str(sys.argv[1]))
        quit()
print('Getting data from year %d to %d' % (start,end))

filename = str(start)+'_to_'+str(end)+'.csv'


offset = 0
table = []
while 1:
    ### Fetch web data from "sports-reference.com"
    page = requests.get('https://www.sports-reference.com/cbb/play-index/tourney.cgi?request=1&match=single&year_min='+str(start)+'&year_max='+str(end)+'&seed_cmp=eq&opp_seed_cmp=eq&game_result=W&pts_diff_cmp=eq&order_by_single=date_game&order_by_combined=g&offset='+str(offset))

    ### Process content, get data table header and body
    soup = bs(page.content,'html.parser')
    th_soup = soup.find_all('thead')
    tb_soup = soup.find_all('tbody')
    if len(tb_soup) == 0:   # No more data to process
        break
    else:
        thead = th_soup[0]
        tbody = tb_soup[0]

    ### Extract table column names
    if len(table) == 0:
        cols = [col.text for col in thead.find_all('th')]
        cols = cols[1:]
        cols.insert(6,'opponent_seed')
        cols.insert(4,'school_seed')
        table = [cols]

    ### Build out table
    for trow in tbody.find_all('tr'):
        # Check if row is invalid
        if trow.has_attr('class'):
            continue

        # Append each item in row
        row = []
        for col in trow.find_all('td'):
            # Split seed and school name
            item = col.text.split('\xa0')

            row.extend(item)

        if len(row) != 13:
            print('ERROR. Too many columns:')
            print(row)

        table.append(row)

    # Increase offset to retrieve next page
    offset += 100

# Save data to .csv file
pd.DataFrame(columns=table[0],data=table[1:]).to_csv('data/'+filename)
print('Data saved to file \'data/%s\'' % filename)

