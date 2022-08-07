import random, time, json

companies = eval(open('.\\company.json','r',encoding='utf-8').read())
lastchange = companies["lastchange"]
stock_setting = eval(open('.\\stock_setting.json','r',encoding='utf-8').read())
max_change = stock_setting["max_change"]
min_change = stock_setting["min_change"]
maxprice = stock_setting["maxprice"]
minprice = stock_setting["minprice"]
cycle =  stock_setting["cycle"]

def change_price():
    current_time = time.time()
    companies["lastchange"] = current_time
    lastchange = current_time

    for company in companies["companies"]:
        prices = companies["companies"][company]
        current = prices[-1]
        org = current

        current += random.randint(min_change,max_change)

        if (current < minprice): current = minprice + random.randint(0,100)
        if (current > maxprice): current = maxprice - random.randint(0,300)

        companies["companies"][company] = [org, current]

    json.dump(companies, open('.\\company.json', 'w', encoding='utf-8'), indent=4,ensure_ascii=False)