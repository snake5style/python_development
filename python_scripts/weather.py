import requests
from bs4 import BeautifulSoup
import pandas as pd

# This script is design to scrape data from the government weather forecast website, then display the results in a csv file.
# created by Ray Fuller


# Setting up page for scraping
page = requests.get('https://forecast.weather.gov/MapClick.php?lat=32.99985910000004&lon=-80.00182459999996#.Xn4ah9-YWV4')
soup = BeautifulSoup(page.content, 'html.parser')

# Creating key variables for scraping
week = soup.find(id='seven-day-forecast')
items = week.find_all(class_='tombstone-container')
period_names = [item.find(class_='period-name').get_text() for item in items]
short_descriptions = [item.find(class_='short-desc').get_text() for item in items]
temperatures = [item.find(class_='temp').get_text() for item in items]

# Setting a pandas to format the collected data
weather_stuff = pd.DataFrame(
    {
      'period': period_names,
      'short_descriptions': short_descriptions,
      'temperatures': temperatures,
    })

# Printing and converting data into a CSV file
print(weather_stuff)

weather_stuff.to_csv('weather.csv')
