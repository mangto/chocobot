import discord, asyncio, datetime, pytz, requests, random
import json, subprocess, threading
from stock_change import *
from  bs4 import BeautifulSoup

#update
open(".\\FMD.py",'w',encoding='utf-8').write(requests.get(url = "https://raw.githubusercontent.com/mangto/kakao-notification/main/FMD.py").text)
from FMD import *
client = discord.Client()

token = "token"
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
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Hello, World!")) #봇의 상메-
    

called = []

@client.event
async def on_message(message):
    def CheckIfEmojied(reaction, user):
        return user == message.author
    companies = eval(open('.\\company.json','r',encoding='utf-8').read())

    if message.content == "초코야":
        called.append(message.author)
        await message.channel.send("네?")

    text = message.content.replace(" ","")
    sender = message.author.name

    if (text == "초코야주식가입" or (text == "주식가입" and message.author in called)):

        if (sender in wallet): await message.channel.send (f"{sender}, 이미 가입이 되어있는걸요?")
        else:
            wallet[sender] = {"money":2000,"stock":{}}

            json.dump(wallet, open('.\\wallet.json', 'w', encoding='utf-8'), indent=4,ensure_ascii=False)

            await message.channel.send (f"{sender}, 가입을 완료했어요!")

    if (text == "초코야지갑" or (text == "지갑" and message.author in called)):
        if (sender in wallet):
            embed = discord.Embed(title=f"{sender}님의 지갑", color=0x96694b)
            embed.add_field(name="잔액", value = f"{str(wallet[sender]['money'])}촠",inline=False)

            stocks = wallet[sender]["stock"]
            if(len(stocks) == 0):
                embed.add_field(name="주식", value = f"비어있다!",inline=False)
            else:
                for stock in stocks:
                    embed.add_field(name=stock, value = f"{wallet[sender]['stock'][stock]}주")

            await message.channel.send (embed=embed)
        else:
            await message.channel.send (f"그치만,, 아직 가입을 안 했는걸요?")
            await message.channel.send (f"'초코야 주식가입' 으로 가입을 해보세요!")

    if ((text == "초코야가격변동" or (text == "가격변동" and message.author in called)) and message.author.guild_permissions.administrator):
        change_price()

    if (text == "초코야주가" or (text == "주가" and message.author in called)):
        embed = discord.Embed(title=f"", color=0x96694b)

        text= ""

        for company in companies["companies"]:
            if (companies['companies'][company][-1] - companies['companies'][company][0] > 0):
                change = " ↑ "
            else:
                change = " ↓ "

            text += f"\n{company} | {change}{companies['companies'][company][-1]}촠"

        text = f"```css{text}```"
        embed.add_field(name="현재 주가",value=text)
        embed.set_footer(text=f"* {int(stock_setting['cycle']-time.time()+companies['lastchange'])}초 뒤에 가격 변동")

        await message.channel.send (embed=embed)

    if (text == "초코야탈퇴" or (text == "탈퇴" and message.author in called)):
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
            await message.channel.send (f"'초코야 주식가입' 으로 가입을 해보세요!")

    if (text.startswith("초코야매수") or (text.startswith("매수") and message.author in called)):
        if (text.startswith("매수")): len_ = 3
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
            embed = discord.Embed(title="매수 방법", description="초코야 매수 <회사> <개수>")
            await message.channel.send(embed=embed)

    if (text.startswith("초코야매도") or (text.startswith("매도") and message.author in called)):
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
            embed = discord.Embed(title="매도 방법", description="초코야 매도 <회사> <개수>")
            await message.channel.send(embed=embed)

    if (text == "!권한"):
        await message.channel.send(str(message.author.guild_permissions.administrator))

    if (message.content != "초코야"):
        if (message.author in called): called.remove(message.author)




#가위바위보 기능

    if message.content == "초코야 가위" or message.content == "초코야 바위" or message.content == "초코야 보":
        random_ = random.randint(1, 3)
        
        if random_ == 1:    # random 에 저장된 변수가 1 (가위 일때)
            if message.content == "초코야 가위":
                await message.channel.send("가위!")
                await message.channel.send("비겼네요!")

            elif message.content == "초코야 바위":
                await message.channel.send("가위!")
                await message.channel.send("앗..제가 졌어요")

            else:
                await message.channel.send("가위!")
                await message.channel.send("훗! 제가 이겼네요!")

        if random_ == 2:    # random 에 저장된 변수가 2 (바위 일때)
            if message.content == "초코야 가위":
                await message.channel.send("바위!")
                await message.channel.send("제가 이겨버렸네요~")

            elif message.content == "초코야 바위":
                await message.channel.send("바위!")
                await message.channel.send("흐음..비겼어요")

            else:
                await message.channel.send("바위!")
                await message.channel.send("힝.. 졌어요.")

        if random_ == 3:    # random 에 저장된 변수가 3 (보 일때)
            if message.content == "초코야 가위":
                await message.channel.send("보!")
                await message.channel.send("뭐..제가 일부러 봐드린건 알죠?")

            elif message.content == "초코야 바위":
                await message.channel.send("보!")
                await message.channel.send("초코가 이겼어요!")

            else:
                await message.channel.send("보!")
                await message.channel.send("아쉽게도 비겼네요.. 한판더해요!")



#초코 일반 기능
    if message.content == "초코야 안녕": # 메세지 감지
        await message.channel.send ("{}, 안녕하세요!".format(message.author.mention))
    if message.content == "초코야 믕":
        await message.channel.send ("므으응..")
    if message.content == "초코야 굴러":
        await message.channel.send ("데굴데굴 구르고 있는 중이에요!")
    if message.content == "초코야 공부해":
        await message.channel.send ("그치만 공부하기 싫은걸요!")
    if message.content == "초코야 숙제해":
        await message.channel.send ("조금 있다가 할게요!")
    if message.content == "초코야 결혼하자":
        await message.channel.send ("청혼은 제가 할게요..💍")
    if message.content == "초코야 이혼하자":
        await message.channel.send ("제가 싫으시다면..초코는 갈게요ㅜㅜ")
    if message.content == "초코야 사귀자":
        await message.channel.send ("초코는 몸이 열개라도 모자라지만..좋아요!")  
    if message.content == "초코야 헤어지자":
        await message.channel.send ("봇은 감정을 느끼진 못하지만..슬픈 말 같아요")  
        
    if message.content == "초코 바보": #메세지 수정기능
        msg = await message.channel.send("바보는 너고요")
        await asyncio.sleep(0.2)
        await msg.edit(content="(초코가 방금 뭐라고 말했나요?)")
    if message.content == "초코 멍청이":
        msg = await message.channel.send("사용자님이 멍청이 아닐까요?")
        await asyncio.sleep(0.2)
        await msg.edit(content="(믕?)")


    if message.content.startswith("초코야 랜덤"):     #랜덤기능
        await message.channel.send (FinalMsgEditor.fullEdit("///FME:Ran:tag///"))
    if message.content.startswith("초코야 배고파"):     #random
        await message.channel.send (FinalMsgEditor.fullEdit("///FME:Ran:hungry///"))
    if message.content.startswith("초코야 사랑해"):     #random
        await message.channel.send (FinalMsgEditor.fullEdit("///FME:Ran:love///"))
    if message.content.startswith("초코야 날씨"):
        await message.channel.send (FinalMsgEditor.fullEdit("기온: ///FME:Crw:temperature///\n날씨: ///FME:Crw:weather///"))


    if message.content == "초코야 임베드": # 메세지 감지
        embed = discord.Embed(title="김초코 사용방법", description="갈구지마세요!",timestamp=datetime.datetime.now(pytz.timezone('UTC')), color=0x96694b)

        embed.add_field(name="임베드 제목 1", value=" 값 ", inline=False)
        embed.add_field(name="임베드 제목 2", value=" 값 ", inline=False) #한문단씩 떨어짐

        embed.add_field(name="임베드 제목 3", value=" 값 ", inline=True)
        embed.add_field(name="임베드 제목 4", value=" 값 ", inline=True) # 2개가 붙여져서 나옴

        embed.set_footer(text="Bot Made by. 준경 #5170", icon_url="https://media.discordapp.net/attachments/826111099271118880/1004280153964294194/1.png?width=677&height=677")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/826111099271118880/1004280153964294194/1.png?width=677&height=677")
        await message.channel.send (embed=embed)


    if message.content == "초코야 도움": 
        embed = discord.Embed(title="도움말", description="명령어에요!", color=0x96694b)
    
        embed.add_field(name="명령어 1", value=" 값 ", inline=False)
        embed.add_field(name="명령어 2", value=" 값 ", inline=False) 
        embed.add_field(name="명령어 3", value=" 값 ", inline=False)
        embed.add_field(name="명령어 4", value=" 값 ", inline=False) 
        embed.add_field(name="명령어 5", value=" 값 ", inline=False) 
        embed.add_field(name="명령어 6", value=" 값 ", inline=False)
        embed.add_field(name="명령어 7", value=" 값 ", inline=False) 

        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1003909846833319977/1004280839347109979/90.png?width=677&height=677")
        await message.channel.send (embed=embed)

    if message.content.startswith ("초코야 공지"):
        await message.channel.purge(limit=1)
        i = (message.author.guild_permissions.administrator)

        if i is True:
            notice = message.content[6:] # 초코야 공지_
            channel = client.get_channel(1003909846833319977) #채널 아이디
            embed = discord.Embed(title="**공지사항**", description="\n――――――――――――――――――――\n\n{}\n\n――――――――――――――――――――".format(notice), color=0x96694b)
            embed.set_footer(text="공지 작성자 : {}".format(message.author), icon_url="https://media.discordapp.net/attachments/1003909846833319977/1004280839347109979/90.png?width=677&height=677")
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1003909846833319977/1004280839347109979/90.png?width=677&height=677")
            await channel.send ("@everyone", embed=embed)
            await message.author.send("**[ BOT 자동 알림 ]** | 정상적으로 공지가 채널에 작성이 완료되었어요! : )\n\n[ 작성  채널 ] : {}\n[ 공지 발신자 ] : {}\n\n[ 내용 ]\n{}".format(channel, message.author, notice))
 
        if i is False:
            await message.channel.send("{}, 관리자 권한이 없어요!".format(message.author.mention))

    if message.content.startswith("초코야 따라해"):
        msg = message.content
        try: exec(str(msg[8:]))
        except: pass
        await message.channel.send (f"{msg[8:]}")

    if message.content.startswith("초코야 급식"):
        msg = message.content.split(" ")
        command = "급식이닷!\n///FME:Caf///"
        if (len(msg) == 4):
            command = f"급식이닷!\n///FME:Caf:{msg[2]}:{msg[3]}///"
        await message.channel.send(FinalMsgEditor.fullEdit(command))

    if message.content.startswith ("초코야 청소"):
        i = (message.author.guild_permissions.administrator)

        if i is True:
            amount = message.content[7:]
            await message.channel.purge(limit=1)
            await message.channel.purge(limit=int(amount))

            embed = discord.Embed(title="**메시지 삭제 알림**", description="채팅 {}개가\n**관리자** {}님의 요청으로 삭제 되었어요!".format(amount, message.author), color=0x96694b)
            embed.set_footer(icon_url="https://media.discordapp.net/attachments/1003909846833319977/1004280839347109979/90.png?width=677&height=677")
            await message.channel.send(embed=embed)
        
        if i is False:
            await message.channel.purge(limit=1)
            await message.channel.send("{}, 명령어를 사용할 수 있는 권한이 없어요!".format(message.author.mention))

# 봇 실행
client.run(token)