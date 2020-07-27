import requests, re, csv
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from prettytable import PrettyTable
from prettytable import from_csv

# This script was design to scrape all european football table results and add them to a csv file. 
# I am current learning more about pandas to apply this data to a postgresql database using django model.
# Created by Ray Fuller


def futbol_index():
   # Website pages to be scraped
    page = [
          'https://www.skysports.com/premier-league-table',
          'https://www.skysports.com/la-liga-table',
          'https://www.skysports.com/bundesliga-table',
          'https://www.skysports.com/serie-a-table',
          'https://www.skysports.com/ligue-1-table'
    ]

    # A list of league abbreviations for naming csv files
    league = [ "EPL", "LIGA", "BUND", "SERIE", "LIGUE", ]

    # Zip for loop get, scrape and parse data into a csv file
    for pag, leag in zip(page, league):
       response = requests.get(pag)
       soup = BeautifulSoup(response.content, 'html.parser')

       top_col = soup.find('tr', attrs={'class': 'standing-table__row'})
       columns = [col.get_text() for col in top_col.find_all('th')]

       last_df = pd.DataFrame(columns=columns)
       last_df

       contents = soup.find_all('tr', attrs={'class':re.compile('standing-table__row')})
       for content in contents:

          teams = [tea.get_text().strip('\n') for tea in content.find_all('td')]
          first_df = pd.DataFrame(teams, columns).T
          first_df.columns=columns

          last_df = pd.concat([last_df,first_df], ignore_index=True)

          last_df.to_csv('{0}.csv'.format(leag), index = False, sep=',', encoding='utf-8')


def main():
   futbol_index()


if __name__ == '__main__':
   main()
