from bs4 import BeautifulSoup
import requests
import json
import re
import sqlite3
import matplotlib.pyplot as plt

cache_name = "cache.json"

def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(cache_name, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(cache_name,"w")
    fw.write(dumped_json_cache)
    fw.close() 

def search_case_number(search_word):
    ''' search a country (fetch or cache) and return case number, death number, and recovery number
    Parameters
    ----------
    search_word: string
        The country name to search
    
    Returns
    -------
    cache_data: dict
        A dictionary that contains the information of a country's case number, death number, and recovery number
    '''
    case_url = "https://www.worldometers.info/coronavirus/country/"+search_word

    cache_dict = open_cache()
    if(case_url in cache_dict.keys()): #cache hit
        print('Using cache')
        cache_data = cache_dict[case_url]
        return cache_data

    else: #cache miss
        print('Fetching')
        response = requests.get(case_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        info = soup.find_all(class_='maincounter-number')
        cache_data = {}
        info = str(info)

        temp = info.split('<div class="maincounter-number"')
        case = int(temp[1][27:-17].replace(",",""))
        death = int(temp[2][8:-16].replace(",",""))
        recover = int(temp[3][31:-15].replace(",",""))

        conn = sqlite3.connect("covid.sqlite")
        cur = conn.cursor()
        create_terms = '''
            CREATE TABLE IF NOT EXISTS "case_table"(
                "country" TEXT,
                "case"	INTEGER,
                "death"	INTEGER,
                "recover"	INTEGER
            );
        '''
        insert_terms = '''
                        INSERT INTO case_table
                        VALUES (?, ?, ?, ?)
        ''' 

        value = [search_word,case,death,recover]
        cur.execute(create_terms)
        cur.execute(insert_terms, value)
        conn.commit()
        cache_data[search_word] = [case,death,recover]
    
        # print(f"Country: {search_word}, Case: {case}, Death: {death}, Recover: {recover}.")
        cache_dict[case_url] = cache_data
        save_cache(cache_dict)
        return cache_data


def search_michigan_vaccine():
    ''' search a county in Michigan (fetch or cache) and return the vaccination data in this county
    Parameters
    ----------
    None
    
    Returns
    -------
    cache_data: dict
        A dictionary that contains the information of a country's vaccination data
    '''
    vaccine_url = "https://data.lansingstatejournal.com/covid-19-vaccine-tracker/michigan/26/"
    cache_dict = open_cache()

    if(vaccine_url in cache_dict.keys()): #cache hit
        print('Using cache')
        cache_data2 = cache_dict[vaccine_url]
        return cache_data2

    else: #cache miss
        print('Fetching')
        response = requests.get(vaccine_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        info = str(soup.find_all(class_='covidcnt table table-condensed table-bordered')).split("<tr><td>")

        cache_data2 = {}

        for i in range(1,len(info)-2):
            #City of Detroit data excluded from Wayne County
            county_name = info[i][info[i].index("<strong>")+8:info[i].index("County")+6]
            population = int(info[i][info[i].index("covd")+6:info[i].index("covc")-22].replace(",",""))
            total_dose = int(info[i][info[i].index("covc")+6:info[i].index("cove")-22].replace(",",""))
            first_dose = int(info[i][info[i].index("cove")+6:info[i].index("covr")-33].replace(",",""))
            first_dose_rate = info[i][info[i].index("covr")-28:info[i].index("covr")-22].replace(",","")
            fully_vaccinated = int(info[i][info[i].index("covr")+6:-22].replace(",",""))
            fully_vaccinated_rate = info[i][-17:-11]

            conn2 = sqlite3.connect("michigan.sqlite")
            cur2 = conn2.cursor()

            create_terms2 = '''
                CREATE TABLE IF NOT EXISTS "michigan_table"(
                    "county_name"	TEXT,
                    "population"	INTEGER,
                    "total_dose"	INTEGER,
                    "first_dose"	INTEGER,
                    "first_dose_rate"	TEXT,
                    "fully_vaccinated"	INTEGER,
                    "fully_vaccinated_rate"	TEXT
                );
            '''

            insert_terms2 = '''
                            INSERT INTO michigan_table
                            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''' 

            value2 = [county_name,population,total_dose,first_dose,first_dose_rate,fully_vaccinated,fully_vaccinated_rate]
            cur2.execute(create_terms2)
            cur2.execute(insert_terms2, value2)
            conn2.commit()
            cache_data2[county_name] = [population,total_dose,first_dose,first_dose_rate,fully_vaccinated,fully_vaccinated_rate]
        cache_dict[vaccine_url] = cache_data2

        save_cache(cache_dict)

        return cache_data2


if __name__ == "__main__":
    print("Inquiry COVID-19 cases data in different countries or vaccination data in the State of Michigan")
    while True:
        choice = input("Which do you want to find? <e.g.: case or vaccination>, input exit to break: ")
        if(choice == 'case' or choice == 'vaccination'):
            if (choice == 'case'):
                search_word = input("Please input the country's name? <e.g.: us>: ")
                res = search_case_number(search_word)
                print(f"Country: {search_word}, total case: {res[search_word][0]}, death: {res[search_word][1]}, recovery: {res[search_word][2]}.")
            elif (choice == "vaccination"):
                vaccine_data = search_michigan_vaccine()
                population_dict = {}
                total_dose_dict = {}
                first_dose_dict = {}
                first_dose_rate_dict = {}
                fully_vaccinated_dict = {}
                fully_vaccinated_rate_dict = {}
                for k,v in vaccine_data.items():
                    population_dict[k] = vaccine_data[k][0]
                    total_dose_dict[k] = vaccine_data[k][1]
                    first_dose_dict[k] = vaccine_data[k][2]
                    first_dose_rate_dict[k] = vaccine_data[k][3]
                    fully_vaccinated_dict[k] = vaccine_data[k][4]
                    fully_vaccinated_rate_dict[k] = vaccine_data[k][5]
                input_type = input("Which type of data are you interested in? Summary or Inquiry: <e.g. summary or inquiry>: ")
                if (input_type == "summary"):
                    data_type = input("Please input the type you are interested in, <e.g. population,total_dose,first_dose,first_dose_rate,fully_vaccinated,fully_vaccinated_rate>: ")
                    if (data_type == "population"):
                        plt.figure(figsize=(15,10))
                        plt.xticks(rotation=270)
                        fig = plt.bar(population_dict.keys(), population_dict.values(), color='g')
                        plt.show()
                    elif (data_type == "total_dose"):
                        plt.figure(figsize=(15,10))
                        plt.xticks(rotation=270)
                        fig = plt.bar(total_dose_dict.keys(), total_dose_dict.values(), color='g')
                        plt.show()
                    elif (data_type == "first_dose"):
                        plt.figure(figsize=(15,10))
                        plt.xticks(rotation=270)
                        fig = plt.bar(first_dose_dict.keys(), first_dose_dict.values(), color='g')
                        plt.show()
                    elif (data_type == "first_dose_rate"):
                        plt.figure(figsize=(15,10))
                        plt.xticks(rotation=270)
                        fig = plt.bar(fully_vaccinated_dict.keys(), fully_vaccinated_dict.values(), color='g')
                        plt.show()
                    elif (data_type == "fully_vaccinated_rate"):
                        plt.figure(figsize=(15,10))
                        plt.xticks(rotation=270)
                        fig = plt.bar(fully_vaccinated_rate_dict.keys(), fully_vaccinated_rate_dict.values(), color='g')
                        plt.show()
                    else:
                        print("Invalid type!")
                elif (input_type == "inquiry"):
                    county = input("Which county are you interested in? <e.g. Alcona County>: ")
                    if county not in vaccine_data:
                        print("Invalid county name!")
                        continue
                    county_data = input("Which type of data are you interested in? <e.g. population,total_dose,first_dose,first_dose_rate,fully_vaccinated,fully_vaccinated_rate>: ")
                    if (county_data == "population"):
                        print(vaccine_data[county][0])
                    elif (county_data == "total_dose"):
                        print(vaccine_data[county][1])
                    elif (county_data == "first_dose"):
                        print(vaccine_data[county][2])
                    elif (county_data == "first_dose_rate"):
                        print(vaccine_data[county][3])
                    elif (county_data == "fully_vaccinated"):
                        print(vaccine_data[county][4])
                    elif (county_data == "fully_vaccinated_rate"):
                        print(vaccine_data[county][5])
                    else:
                        print("Invalid input.")
                else:
                    print("Invalid input, please try again!")

        elif (choice == "exit"):
            break

        else:
            print("Invalid input, please try again!")