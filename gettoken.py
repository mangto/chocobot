code = open(".\\bot.py",'r',encoding='utf-8').read().splitlines()
tokened = [a for a in code if "client.run" in a]
token = tokened[0][12:-2]

print(token)