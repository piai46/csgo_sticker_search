import requests, json
from time import sleep 
from random_user_agent.user_agent import UserAgent
from datetime import datetime

stickers = [
    'Titan Katowice 2015',
    "Cloud9 G2A Katowice 2015",
    "Natus Vincere Katowice 2015",
    "HellRaisers Katowice 2015",
    "Vox Eminor Katowice 2015",
    "LGB eSports Katowice 2015",
    "3DMAX Katowice 2015",
    "Flipsid3 Tactics Katowice 2015",
    "Flipsid3 Tactics MLG Columbus 2016",
    "Luminosity Gaming holo MLG Columbus 2016",
    "Flipsid3 Tactics holo MLG Columbus 2016",
    "Team Liquid holo MLG Columbus 2016",
    "Vox Eminor Cologne 2014",
    "iBUYPOWER Cologne 2014",
    "Titan Cologne 2014",
    "100 Thieves Boston 2018",
    "Flipsid3 Tactics holo Cologne 2016",
    "FaZe Clan holo Cologne 2016",
    "SK Gaming holo Cologne 2016",
    "Battle Scarred holo",
    "Lambda holo",
    "Team Liquid Atlanta 2017",
    "HellRaisers Atlanta 2017",
    ]

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
    cookies = {'cookie':'ActListPageSize=100; timezoneOffset=-10800,0; _ga=GA1.2.535929133.1603673925; Steam_Language=english; browserid=2371685853297177240; steamMachineAuth76561198080126414=3976CD0E0052D96FDE6ADC15C591862E0FA94496; rgDiscussionPrefs={"cTopicRepliesPerPage":50}; steamCurrencyId=7; recentlyVisitedAppHubs=438740,12210,447500,433850,892970,985810,1213740,252950,731490,895400,1271700,1623660,730,1549180,846770,1284210,413150,108600,1403370,1591520; steamRememberLogin=76561198837076030||22bcdb33cb3368ca74501a04f4bc953f; steamMachineAuth76561198837076030=9BB6F9755C39E717F546A4375525C34E4CFF0209; _gid=GA1.2.759725383.1646319405; strInventoryLastContext=730_2; sessionid=6ec85ce666f39e835b4585c9; webTradeEligibility={"allowed":1,"allowed_at_time":0,"steamguard_required_days":15,"new_device_cooldown_days":7,"time_checked":1646619868}; steamLoginSecure=76561198837076030||F01AB5FF73348E3442E6086D32B05A99D6649CD4; steamCountry=BR|a09c01f022e5408e0f3428576974a68c; rgTopicView_General_4009259_1={"620703493331692216":1646664966,"616188473088925567":1646665003}; tsTradeOffersLastRead=1641085466'}
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
                        print(f'{skin_name} current price: R${skin_price_now} announced price: R${announced_price} +{difference}% {sticker}')
        else:
            skin_info = skin_price(skin_name)
            try:
                skin_price_now = float(skin_info['lowest_price'].replace('R$ ', '').replace(',', '.'))
            except:
                skin_price_now = float(skin_info['median_price'].replace('R$ ', '').replace(',', '.'))
            difference = compare_prices(skin_price_now, announced_price)
            if difference <= 40:
                print(f'{skin_name} current price: R${skin_price_now} announced price: R${announced_price} +{difference}% {sticker}')
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
    if today_date == file_data['date']:
        price_update = True
        print('Updated price!')
    else:
        price_update = False
        clear_file(today_date)
        print('Price not updated!')
    for sticker in stickers:
        print(f'Searching {sticker}')
        items = sticker_search(sticker)
        for item in items['results']:
            handle_item(item, sticker, updated=price_update)
    if price_update == False:
        update_date(today_date)
        print('All prices have been updated!')

if __name__ == '__main__':
    main()