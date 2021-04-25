# COVID-19 Case/Death/Recovery & Vaccination Data in Michigan

# Installation: 
Necessary things:
* python
* beautifulsoup4
* requests
* sqlite3
* matplotlib

# Functions: 
**Search the case/death/recovery data in different countries:** You can simply input the country's name you want to inquiry, and then the corresponding data will be obtained, and they will be saved in a sqlite database automatically. Cache will also be used.
**Search the vaccination data in a Michigan county:** You can find the vaccination data (for example: fully vaccinated rate) in each of county in Michigan. The whole dataset obtained will be saved in a sqlite database. Cache will also be used.

# Data Proparation
COVID-19 cases data was scrapped from WorldMeter(https://www.worldometers.info/coronavirus/); Michigan vaccination data was scrapped from Lansing State Journal (https://data.lansingstatejournal.com/covid-19-vaccine-tracker/michigan/26/)

# Interaction and Presentation
In vaccination data part, several summarized figures will be shown to you based on your own interest, including a comparison of first dose rate in different Michigan counties, etc.
