import requests, json
from time import sleep 
from random_user_agent.user_agent import UserAgent
from datetime import datetime

stickers = [
    'Titan Katowice 2015',
    "Titan Cologne 2014",
    "Cloud9 G2A Katowice 2015",
    "Natus Vincere Katowice 2015",
    "HellRaisers Katowice 2015",
    "HellRaisers Atlanta 2017",
    "Vox Eminor Katowice 2015",
    "Vox Eminor Cologne 2014",
    "LGB eSports Katowice 2015",
    "3DMAX Katowice 2015",
    "Flipsid3 Tactics Katowice 2015",
    "Flipsid3 Tactics MLG Columbus 2016",
    "Flipsid3 Tactics holo Cologne 2016",
    "Flipsid3 Tactics Krakow 2017",
    "Flipsid3 Tactics Atlanta 2017" ,
    "Flipsid3 Tactics holo MLG Columbus 2016",
    "Luminosity Gaming Cologne 2015",
    "Luminosity Gaming holo MLG Columbus 2016",
    "Luminosity Gaming MLG Columbus 2016",
    "Team Liquid holo MLG Columbus 2016",
    "Team Liquid Atlanta 2017",
    "Team Liquid Boston 2018",
    "iBUYPOWER Cologne 2014",
    "100 Thieves Boston 2018",
    "FaZe Clan holo Cologne 2016",
    "SK Gaming Cologne 2016",
    "SK Gaming holo Cologne 2016",
    "SK Gaming Krakow 2017",
    "SK Gaming Boston 2018",
    "SK Gaming Atlanta 2017",
    "Astralis Atlanta 2017",
    "Battle Scarred holo",
    "Lambda holo",
    ]

items_to_ignore = ['Sealed Graffiti', 'Sticker Capsule']

cookies = {'cookie':'insert the cookies here'}

def skin_price(skin_name):
    user_agent_rotator = UserAgent()
    user_agent = user_agent_rotator.get_random_user_agent()
    headers = {'User-Agent':user_agent}
    payload = {"appid": "730", "market_hash_name": skin_name, "currency": "7"}
    response = requests.get("http://steamcommunity.com/market/priceoverview", payload, headers=headers).json()
    if response == None or response['success'] == False:
        print('Cooldown... 10s')
        sleep(10)
        skin_price(skin_name)
    sleep(10)
    return response

def sticker_search(sticker_name):
    payload = {'query':f'"{sticker_name}"', 'start':'0', 'count':'15', 'search_descriptions':'1', 'sort_column':'price', 'sort_dir':'asc', 'appid':'730', 'norender':'1', 'currency':'7'}
    response = requests.get('https://steamcommunity.com/market/search/render/?', payload, cookies=cookies)
    if response.json() == None:
        print('Cooldown... 10s')
        sleep(10)
        sticker_search(sticker_name)
    sleep(10)
    return response.json()

def handle_item(item, sticker, updated):
    file_data = open_skin_prices()
    skin_name = item['name']
    for item_ignore in items_to_ignore:
        if item_ignore in skin_name:
            return
    announced_price = float(item['sell_price_text'].replace('R$ ', '').replace(',', '.'))
    if announced_price <= 20:
        skin_price_file = check_skin(skin_name)
        if skin_price_file == True and updated == True:
            for item_file in file_data['skin']:
                if skin_name == item_file['skin_name']:
                    try:
                        skin_price_now = float(item_file['lowest_price'].replace('R$ ', '').replace(',', '.'))
                    except:
                        skin_price_now = float(item_file['median_price'].replace('R$ ', '').replace(',', '.'))
                    difference = compare_prices(skin_price_now, announced_price)
                    if difference <= 40:
                        print(f'\n{skin_name} \ncurrent price: R${skin_price_now} announced price: R${announced_price} +{difference}%')
        else:
            skin_info = skin_price(skin_name)
            try:
                skin_price_now = float(skin_info['lowest_price'].replace('R$ ', '').replace(',', '.'))
            except:
                skin_price_now = float(skin_info['median_price'].replace('R$ ', '').replace(',', '.'))
            difference = compare_prices(skin_price_now, announced_price)
            if difference <= 40:
                print(f'\n{skin_name} \ncurrent price: R${skin_price_now} announced price: R${announced_price} +{difference}%')
            if 'lowest_price' in skin_info.keys():
                data_to_file = {
                    'skin_name':skin_name, 
                    'success': skin_info['success'],
                    'lowest_price': skin_info['lowest_price']
                    }
            else:
                data_to_file = {
                    'skin_name':skin_name, 
                    'success': skin_info['success'],
                    'median_price': skin_info['median_price']
                    }
            add_price_to_file(data_to_file)

def open_skin_prices():
    with open('skin_price.json', 'r') as f:
        data = json.load(f)
        f.close()
    return data

def write_skin_prices(content):
    with open('skin_price.json', 'w') as f:
        json.dump(content, f)
        f.close()

def add_price_to_file(data):
    file_data = open_skin_prices()
    file_data['skin'].append(data)
    write_skin_prices(file_data)

def check_skin(skin_name):
    data = open_skin_prices()['skin']
    skins = [list(skin.values())[0] for skin in data]
    if skin_name in skins:
        return True
    return False

def compare_prices(current_price, announced_price):
    difference = round(((announced_price*100)/current_price)-100, 2)
    return difference

def update_date(date):
    data = open_skin_prices()
    data['date'] = date
    write_skin_prices(data)

def clear_file(date):
    data = {"date":date,"skin": [{
        "skin_name": "AK-47 | Point Disarray (Factory New)",
        "success": True,
        "lowest_price": "R$ 172,50",
        "volume": "48",
        "median_price": "R$ 167,38"
    },]}
    write_skin_prices(data)

def main():
    file_data = open_skin_prices()
    today_date = datetime.now().strftime('%d/%m')
    count = 0
    if today_date == file_data['date']:
        price_update = True
        print('Updated price!')
    else:
        price_update = False
        clear_file(today_date)
        print('Price not updated!')
    for sticker in stickers:
        count += 1
        print(50*'-')
        print(f'({count}/{len(stickers)})Searching {sticker}')
        items = sticker_search(sticker)
        for item in items['results']:
            handle_item(item, sticker, updated=price_update)
        print(50*'-')
    if price_update == False:
        update_date(today_date)
        print('All prices have been updated!')
    print('Press any button to exit...')
    input()

if __name__ == '__main__':
    try:
        main()
    except:
        input()