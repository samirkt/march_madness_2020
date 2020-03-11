'''
Samir Townsley
March 3, 2020
NCAA Season Data Scraper

Description: 
    Get season stats by team
Usage: 
    Run with default parameters - python3 get_season_data.py
Source:
    www.sports-reference.com
'''



from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import sys, os

### Set year parameters
if len(sys.argv) == 1:  # Default year range
    start = 1987    # Introduction of 3-pt line and shot clock
    end = 2019
else:   # Manual year entry
    if sys.argv[1] == '1':
        start = input('Enter start year: ')
        end = input('Enter end year: ')
        print()
    else:
        print('Error: Invalid argument \'%s\'' % str(sys.argv[1]))
        quit()
print('Getting data from year %s through %s' % (start,end))

 ### Create data directory and file name
data_dir = 'data'
sub_dir = data_dir+'/season'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)
if not os.path.exists(sub_dir):
    os.mkdir(sub_dir)
filename = sub_dir+'/'+str(start)+'_to_'+str(end)+'.csv'


table = []
for year in range(int(start),int(end)+1):
    ### Status report
    print('\tCurrent year: '+str(year), end="\r", flush=True)

    ### Fetch web data from "sports-reference.com"
    page = requests.get('https://www.sports-reference.com/cbb/seasons/'+str(year)+'-school-stats.html')

    ### Process content, get data table headers and body
    soup = bs(page.content,'html.parser')
    thead = soup.find_all('thead')[0]
    tbody = soup.find_all('tbody')[0]

    ### Extract table column names
    if len(table) == 0:
        cols = []
        headers = thead.find_all('tr')
        for over in headers[0].find_all('th'): # Get high-level columns
            val = over.get('colspan')
            cnt = 1 if val is None else int(val)
            cols.extend([over.text]*cnt)
        for i,under in enumerate(headers[1].find_all('th')): # Combine with sub-columns
            cols[i] = cols[i]+'_'+under.text
        table = [['year']+cols[1:]]

    ### Build out table
    for trow in tbody.find_all('tr'):
        # Check if row is invalid
        if trow.has_attr('data-row'):
            continue

        # Append each item in row
        row = []
        for col in trow.find_all('td'):
            # Split school name and ncaa appearance
            item = col.text.split('\xa0')

            row.extend(item)

        # Check if team was in NCAA tourney
        if len(row) > 0 and row[1] == 'NCAA':
            table.append([year]+row[:1]+row[2:])





### Save data to .csv file
pd.DataFrame(columns=table[0],data=table[1:]).to_csv(filename)
print('\n\nData saved to file \'%s\'' % filename)

