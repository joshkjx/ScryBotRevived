import urllib
import requests as rq

### function that takes a search string (must have no spaces!) and queries scryfall API, returning a Search object, which is a json containing a list of Card objects.
### Even if there is only a single result, it's still stored in a list!
### Access the cards by doing output['data']
### If output is paginated, the GET uri for the next page is found in output['next_page']

async def get_card_info(query = str):
    url_encoded_query = urllib.parse.quote_plus(query)
    request_query = 'https://api.scryfall.com/cards/search?q=' + url_encoded_query
    response = rq.get(request_query)
    if response.status_code == 200:
        output = response.json()
    else:
        return "Error"
    return output

    
## scryfall data fulltext print logic
async def ask_scryfall(query: str):
    response = await get_card_info(query)
    if response == "Error":
        return 'Something went wrong!'
    cardlist = response['data']
    if len(cardlist) > 1:
        out_text = 'More than one card found, please try another search with one of the following:'
        for i in range(len(cardlist)):
            out_text += '\n' + cardlist[i]['name']
            if i > 30:
                out_text += '...' + '\nMore than 30 entries, please refine your search.'
                break
        out_text += '\nIf you\'re looking for an exact match, you can add ! before the name to search for a match for an exact name. (e.g. /scry !greed)'
        return out_text
    else:
        cardobj = response['data'][0]
        card_name = '*' + cardobj['name'] + '*'
        out_text = card_name
        cardfaces = list()
        if 'card_faces' in cardobj:
            for i in cardobj['card_faces']:
                cardfaces.append(i)
        else:
            cardfaces.append(cardobj)
        for i in range(len(cardfaces)):
            out_text += '\n'
            out_text += (cardfaces[i]['mana_cost'].replace('{', '').replace('}','') + '\n')
            out_text += ('_' + cardfaces[i]['type_line'] + '_' + '\n')
            out_text += (cardfaces[i]['oracle_text'].replace('(','_(').replace(')',')_') + '\n')
            if "Creature" in cardfaces[i]['type_line']:
                out_text += (cardfaces[i]['power'] + '/' + cardfaces[i]['toughness'])
            elif "Planeswalker" in cardfaces[i]['type_line']:
                out_text += 'Starting Loyalty: ' + cardfaces[i]['loyalty']
            if i >= (len(cardfaces) - 1):
                break
            out_text += "\n --------"
        return out_text


# Logic for the price fetching
async def fetch_prices(cardlist):
    price_cats = {'usd' : 'USD', 'usd_foil' : 'USD (Foil)', 'usd_etched': 'USD (Etched)'}
    if len(cardlist) > 1:
        out_text = 'More than one card found, please try another search with one of the following:'
        for i in range(len(cardlist)):
            out_text += '\n' + cardlist[i]['name']
            if i > 30:
                out_text += '...' + '\nMore than 30 entries, please refine your search.'
                break
        out_text += '\n\nIf you\'re looking for an exact match, you can add ! before the name to search for a match for an exact name. (e.g. /scry !greed)'
        return out_text
    out_text = "Today's prices of *{cardname}* are: \n| ".format(cardname = cardlist[0]['name'])
    pricelist = cardlist[0]['prices']
    for currency in price_cats:
        out_text += ("*" + price_cats[currency] + "*: ")
        if pricelist[currency]:
            out_text += str(pricelist[currency])
        else:
            out_text += "N/A"        
        out_text += ' | '
    out_text += '\nPlease note that these prices are updated once a day, not in real time.'
    return out_text