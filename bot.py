import discord, asyncio, datetime, pytz, requests, random
import json, subprocess, threading
from stock_change import *
from  bs4 import BeautifulSoup

client = discord.Client()

token = "ODQwMDE4NTUyMzUwMzEwNDEw.G78O01.iXjfBiIOdwWZlKIVEuW9LqYd-Tx1O_jOyiZa08"
wallet = eval(open('.\\wallet.json','r',encoding='utf-8').read())
companies = eval(open('.\\company.json','r',encoding='utf-8').read())
stock_setting = eval(open('.\\stock_setting.json','r',encoding='utf-8').read())

def starter(): 
    subprocess.call(f'python change_loop.py', shell=True)
threading.Thread(target=starter).start()

class emoji:
    yes = "⭕"
    no = "❌"


@client.event
async def on_ready(): # 봇이 실행되면 한 번 실행됨
    print("봇이 실행되었습니다")
    await client.change_presence(status=discord.Status.online, activity=discord.Game("STOCK UPDATE")) #봇의 상메-
    

called = []

@client.event
async def on_message(message):
    def CheckIfEmojied(reaction, user):
        return user == message.author
    companies = eval(open('.\\company.json','r',encoding='utf-8').read())

    if message.content == "델루야":
        called.append(message.author)
        await message.channel.send("네?")

    text = message.content.replace(" ","")
    sender = message.author.name

    if (text == "델루야주식가입" or (text == "주식가입" and message.author in called)):

        if (sender in wallet): await message.channel.send (f"{sender}, 이미 가입이 되어있는걸요?")
        else:
            wallet[sender] = {"money":2000,"stock":{}}

            json.dump(wallet, open('.\\wallet.json', 'w', encoding='utf-8'), indent=4,ensure_ascii=False)

            await message.channel.send (f"{sender}, 가입을 완료했어요!")

    if (text == "델루야지갑" or (text == "지갑" and message.author in called)):
        if (sender in wallet):
            embed = discord.Embed(title=f"{sender}님의 지갑", color=0x96694b)
            embed.add_field(name="💰 보유 금액", value = f"{str(wallet[sender]['money'])}촠",inline=False)

            stocks = wallet[sender]["stock"]
            text = ""
            if(len(stocks) == 0):
                text = "비어있다!"
            else:
                for stock in stocks:
                    text += f"\n{stock} | {wallet[sender]['stock'][stock]}주"

            text = f"```{text}```"
            embed.add_field(name="📃 보유 주식", value = text)

            await message.channel.send (embed=embed)
        else:
            await message.channel.send (f"그치만,, 아직 가입을 안 했는걸요?")
            await message.channel.send (f"'델루야 주식가입' 으로 가입을 해보세요!")

    if ((text == "델루야가격변동" or (text == "가격변동" and message.author in called)) and message.author.guild_permissions.administrator):
        change_price()

    if (text == "델루야주가" or (text == "주가" and message.author in called)):
        embed = discord.Embed(title=f"", color=0x96694b)

        text= ""

        for company in companies["companies"]:
            if (companies['companies'][company][-1] - companies['companies'][company][0] > 0):
                change = " ↑ "
            else:
                change = " ↓ "

            if (len(str(companies['danger'][company])) <= 3):
                text += f"\n{company} ({companies['danger'][company]}%)  | {change}{companies['companies'][company][-1]}촠"
            else:
                text += f"\n{company} ({companies['danger'][company]}%) | {change}{companies['companies'][company][-1]}촠"

        text = f"```css{text}```"
        embed.add_field(name="현재 주가",value=text)
        embed.set_footer(text=f"* {int(stock_setting['cycle']-time.time()+companies['lastchange'])}초 뒤에 가격 변동")

        await message.channel.send (embed=embed)

    if (text == "델루야탈퇴" or (text == "탈퇴" and message.author in called)):
        if (sender in wallet):
            embed = discord.Embed(title="탈퇴를 진행합니다", description="아래의 이모지에 반응해주세요", color=0x96694b)
            msg = await message.channel.send(embed=embed)

            await msg.add_reaction(emoji.yes)
            await msg.add_reaction(emoji.no)

            try:
                reaction = await client.wait_for("reaction_add", check=CheckIfEmojied, timeout=15)
                reaction = reaction[0]
                    
                if reaction.emoji == emoji.yes:
                    await msg.delete()
                    del wallet[sender]
                    await message.channel.send("탈퇴처리가 정상적으로 완료되었습니다")
                    json.dump(wallet, open('.\\wallet.json', 'w', encoding='utf-8'), indent=4,ensure_ascii=False)

                elif reaction.emoji == emoji.no:
                    await msg.delete()
                    await message.channel.send("탈퇴가 취소 되었습니다")

            except asyncio.exceptions.TimeoutError:
                await msg.delete()
                await message.channel.send("시간이 초과되었습니다")
        else:
            await message.channel.send (f"그치만,, 아직 가입을 안 했는걸요?")
            await message.channel.send (f"'델루야 주식가입' 으로 가입을 해보세요!")

    if (text.startswith("델루야매수") or (text.startswith("매수") and message.author in called)):
        if (text.startswith("매수")): len_ = 3
        else: len_ = 4

        tokened = message.content.split(" ")
        if (len(tokened) == len_):
            company = tokened[len_-2]
            count = tokened[len_-1]
            
            print(count)

            if (count.isdigit() == False and count != "올인"):
                await message.channel.send("잘못된 개수에요!")

            else:
                current_money = wallet[sender]["money"]
                current_price = companies["companies"][company][-1]
                if (count == "올인"):
                    count = int(current_money/current_price)
                count = int(count)
                current_money = wallet[sender]["money"]

                if (company not in companies["companies"]):
                    await message.channel.send("그.. 어디 회사라고요?")
                
                else:
                    if (current_money >= current_price * count):
                        wallet[sender]["money"] -= current_price * count

                        if (company in wallet[sender]["stock"]):
                            wallet[sender]["stock"][company] += count
                        else:
                            wallet[sender]["stock"][company] = count
                        

                        json.dump(wallet, open('.\\wallet.json', 'w', encoding='utf-8'), indent=4,ensure_ascii=False)

                        await message.channel.send(f"{company}의 주식 {count}주를 매수했어요!")

                    else:
                        await message.channel.send("돈이 부족해요!")

        else:
            embed = discord.Embed(title="매수 방법", description="델루야 매수 <회사> <개수>")
            await message.channel.send(embed=embed)

    if (text.startswith("델루야매도") or (text.startswith("매도") and message.author in called)):
        if (text.startswith("매도")): len_ = 3
        else: len_ = 4

        tokened = message.content.split(" ")
        if (len(tokened) == len_):
            company = tokened[len_-2]
            count = tokened[len_-1]

            if (count.isdigit() == False):
                await message.channel.send("잘못된 개수에요!")

            else:
                count = int(count)
                current_money = wallet[sender]["money"]
                current_price = companies["companies"][company][-1]

                if (company in wallet[sender]["stock"]):
                    having_count = wallet[sender]["stock"][company]

                    if (company not in companies["companies"]):
                        await message.channel.send("그.. 어디 회사라고요?")
                    
                    else:
                        if (having_count >= count):
                            wallet[sender]["money"] += current_price * count

                            if (having_count == count):
                                del wallet[sender]["stock"][company]

                            else:
                                wallet[sender]["stock"][company] -= count


                            json.dump(wallet, open('.\\wallet.json', 'w', encoding='utf-8'), indent=4,ensure_ascii=False)
                            await message.channel.send(f"{company}의 주식 {count}주를 매도했어요!")
                else:
                    await message.channel.send("그치만 그 회사의 주식을 보유하지 않고 있는걸요?")

        else:
            embed = discord.Embed(title="매도 방법", description="델루야 매도 <회사> <개수>")
            await message.channel.send(embed=embed)

    if (text == "!권한"):
        await message.channel.send(str(message.author.guild_permissions.administrator))

    if (message.content != "델루야"):
        if (message.author in called): called.remove(message.author)






# 봇 실행
client.run(token)