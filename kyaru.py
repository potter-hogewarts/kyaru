# インストールした discord.py を読み込む
from multiprocessing.sharedctypes import Value
import discord
import random
import time
import asyncio
from typing import Optional
from discord.utils import get
import deepl
from discord.ext import tasks
import matplotlib.pyplot as plt
import collections
import numpy as np
import os

# 自分のBotのアクセストークンに置き換えてください
TOKEN = os.getenv('TOKEN')


intents=discord.Intents.all()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

class Janken(discord.ui.View):
    def __init__(self,):
        hands = ['グー','チョキ','パー']
        super().__init__(timeout=5.0)
        #サーバー内の全てのチャンネルを取得してHugaListの引数に格納する
        for hand in hands:
            self.add_item(JankenBot(hand))

class JankenBot(discord.ui.Button):
    def __init__(self,hand:str):
        super().__init__(label=hand,style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        #コンピュータが勝敗時に送る画像とメッセージ
        result_images = ['https://cdn-ak.f.st-hatena.com/images/fotolife/k/kanisanhimazin/20200415/20200415171232.jpg','https://pbs.twimg.com/media/EWn0dLFU4AUGSMR.jpg','https://pbs.twimg.com/media/El8mduPVMAI7wqj.jpg:small'] 
        result_msg = ""
        result_image = ""
        #プレイヤーが押した手
        player_hand = self.label

        #コンピュータが出す手
        hands = ['./janken_gu.png','./janken_choki.png','./janken_pa.png']
        cmp_hand = hands[random.randrange(3)]

        #じゃんけん勝敗
        #じゃんけん勝った時
        if (player_hand == 'グー' and cmp_hand == hands[2]) or (player_hand == 'チョキ' and cmp_hand == hands[0]) or (player_hand == 'パー' and cmp_hand == hands[1]):
            result_msg = "私の勝ちです"
            result_image = result_images[0]

        #じゃんけ負けた時
        if(player_hand == 'グー' and cmp_hand == hands[1]) or (player_hand == 'チョキ' and cmp_hand == hands[2]) or (player_hand == 'パー' and cmp_hand == hands[0]):
            result_msg = "あなたの勝ちです"
            result_image = result_images[1]

        #あいこの時
        if(player_hand == 'グー' and cmp_hand == hands[0]) or (player_hand == 'チョキ' and cmp_hand == hands[1]) or (player_hand == 'パー' and cmp_hand == hands[2]):
            result_msg = "あいこです"
            result_image = result_images[2]

        #file=discord.File(r'c:\location\of\the_file_to\send.png')

        #コンピュータが手を出す
        file = discord.File(cmp_hand,filename="hand.png")
        embed = discord.Embed(title='ポン')
        embed.set_image(url="attachment://hand.png")
        await interaction.response.send_message(file=file, embed=embed, ephemeral=True)
        
        #数秒待つ
        time.sleep(1.12)

        #リザルト
        embed = discord.Embed(title = result_msg)
        embed.set_image(url=result_image)
        await interaction.followup.send(embed = embed,ephemeral=True)
        #return self.values[0]


# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')
    #await greet() # 挨拶する非同期関数を実行
    await client.change_presence(activity=discord.Game(name="XXX"))
    await tree.sync()
    detect_member.start()


@tree.command(
    name="log",#コマンド名
    description="ログファイルを出力(管理者権限)"#コマンドの説明
)
@discord.app_commands.default_permissions(
    administrator=True
)
async def log(interaction: discord.Interaction):
    await interaction.response.send_message(file=discord.File('./kyaru.log'),ephemeral=True)


class Button(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ButtonReact("集計"))
        self.add_item(ButtonReact("削除"))
        

class ButtonReact(discord.ui.Button):
    def __init__(self,txt:str):
        super().__init__(label=txt,style=discord.ButtonStyle.blurple)
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="処理中...",ephemeral=True)
        if self.label == "集計":
            #process
            anrs=[]
            fig = plt.figure()
            poll = interaction.message
            print(poll)
            for ans in interaction.message.poll.answers:
                anrs.append(ans.text)
                c = collections.Counter(anrs)
                labels = np.array(list(c.keys()))
                values = np.array(list(c.values()))
                plt.pie(values,labels=labels)
                fig.savefig("./pie.jpg")
                embed = discord.Embed(title="集計結果")
                fname = "pie.jpg" # アップロードするときのファイル名 自由に決めて良いですが、拡張子を忘れないように
                file = discord.File(fp="./pie.jpg",filename=fname,spoiler=False) # ローカル画像からFileオブジェクトを作成
                embed.set_image(url=f"attachment://{fname}") # embedに画像を埋め込むときのURLはattachment://ファイル名
                await interaction.followup.send(file=file, embed=embed,ephemeral=True) # ファイルとembedを両方添えて送信する
                
        if self.label == "削除":
            #process
            await interaction.message.delete()
	
@tree.command(
    name="poll"
)
@discord.app_commands.describe(
    qs="質問文"
)
@discord.app_commands.describe(
    ans="選択肢の候補「,」で区切る"
)
async def poll(interaction:discord.Interaction,qs:str,ans:str):
    await interaction.response.send_message(content="作成中...",ephemeral=True)
    embed=discord.Embed(title=qs)
    try:
        ans.split(',')
        ch=ord("a")
        for s in ans.split(","):
            embed.add_field(name=f":regional_indicator_{chr(ch)}:"+":"+s,value="",inline=False)
            ch += 1
    except Exception as e:
        print(e)

    button = Button()
    msg = await interaction.channel.send(embed=embed,view=button)
    for c in range(ord('a'), ch):
        #print(127365+c)
        await msg.add_reaction(chr(127365+c))

    return


@tasks.loop(seconds=900)
@client.event
async def detect_member():
    #HogewartsサーバーID
    gld = client.get_guild(1111111111111111111)

    #メンバー数チャンネル
    chnl = client.get_channel(22222222222222222222)

    await chnl.edit(name="👥メンバー数:" + str(gld.member_count))
    bot_count = sum(1 for member in gld.members if member.bot)

    #ボットの数チャンネル
    chnl = client.get_channel(3333333333333333333333)
    await chnl.edit(name="🤖ボットの数:" + str(bot_count))

    #学生数のチャンネル
    chnl = client.get_channel(44444444444444444444444)
    await chnl.edit(name="👤学生数:" + str(gld.member_count - bot_count))

    #チャンネル数のチャンネル
    chnl = client.get_channel(5555555555555555555555)
    await chnl.edit(name="💭チャンネル数:" + str(len(gld.channels)))

    #ロールの数のチャンネル
    chnl = client.get_channel(6666666666666666666666)
    await chnl.edit(name="📚ロールの数:" + str(len(gld.roles)))
    return

class TimerIsActive(Exception):
    pass  #  タイマーが動いているときの例外

class TimerManager:
    _timer: Optional[asyncio.Task] = None  #  現在動いているタイマー ( None ならば動いていない)

    @staticmethod
    def _timer_reset(task):
        TimerManager._timer = None  #  タイマーを消去

    @staticmethod
    async def timer_start(second: int):
        if TimerManager.is_active():
            raise TimerIsActive("タイマーがすでに動いています。")
        TimerManager._timer = asyncio.create_task(asyncio.sleep(second))  #  タイマーの Task を保持
        TimerManager._timer.add_done_callback(TimerManager._timer_reset)  #  タイマーが終わったら消去する
        await TimerManager._timer  #  タイマーが終わるのを待つ

    @staticmethod
    def is_active():
        return TimerManager._timer is not None


@tree.command(
    name="ub"#コマンド名
)
@discord.app_commands.default_permissions(
    administrator=True
)
async def ub(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("削除",ephemeral=True)
        await interaction.channel.purge()
        return
    else:
        await interaction.response.send_message('管理人のみ操作可能です',ephemeral=True)
        return

@tree.command(
    name="janken" #コマンド名
)
async def janken(interaction: discord.Interaction):
    await interaction.response.send_message("じゃんけん",ephemeral=True)
    time.sleep(1.2)
    await interaction.followup.send("最初はグー！",ephemeral=True)
    time.sleep(1.2)
    await interaction.followup.send("じゃんけん...",view = Janken(),ephemeral=True)

    return


@tree.command(
    name="slot",#コマンド名
)
async def slot(interaction: discord.Interaction):
    kakuritu = random.randint(1, 11)
    slot_list = ['\U00002660', '\U00002663', '\U00002665', '\U00002666', ':seven:']
    A = random.choice(slot_list)
    B = random.choice(slot_list)
    C = random.choice(slot_list)
    if int(kakuritu) == int(1):
        await interaction.response.send_message("ボーナス確定!!!",ephemeral=True)
        time.sleep(3)#3秒間待つ
        await interaction.followup.send(":seven:"+":seven:"+":seven:",ephemeral=True)#7だけ出るように指定
        return
    else:
        await interaction.response.send_message("%s%s%s" % (A, B, C),ephemeral=True)
        return

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    if message.author.id == 302050872383242240:
        if TimerManager.is_active():
            return  #  タイマーがすでに動いているので

        await message.channel.send("タイマー開始!" + str(120) + "分後にbumpの通知")
        await TimerManager.timer_start(120*60)
        await message.channel.send("bump")


    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return


@client.event
async def on_raw_reaction_add(payload):
    # 絵文字と国の辞書
    emojiDict = {"🇯🇵" : "ja", "🇺🇸" : "EN-US", "🇭🇺" : "hu", "🇪🇸" : "es", "🇫🇷" : "FR", "🇰🇷":"ko","🇩🇪":"de","🇨🇳":"zh","🇵🇹":"PT-PT"}

    # 返信するため emoji から メッセージオブジェクトを取得
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    
    
    reaction = get(message.reactions, emoji=payload.emoji.name)

    if reaction != None and payload.emoji.name in emojiDict and reaction.count == 1:
        translator = deepl.Translator("DEEPL TOKEN") 
        result = translator.translate_text(message.content, target_lang=emojiDict[payload.emoji.name]) 
        translated_text = result.text
        
        for i in range(0,len(message.content),1000):
            if translated_text[i:i+1000] == "":
                return
            #翻訳前と後を表示
            
            #print("translate:",type(translated_text[i:i+1000]))
            embed = discord.Embed(title="result of translate")
            embed.add_field(name='message', value=message.content[i:(1024-len(translated_text[i:i+1000]))])
            embed.add_field(name='translate',value=translated_text[i:i+1000],inline=False)
            await message.channel.send(embed=embed)

@client.event
async def on_voice_state_update(member, before, after):
    name = member.nick
    if name == None:
        name = member.name
    # チャンネルへの入室ステータスが変更されたとき（ミュートON、OFFに反応しないように分岐）
    if before.channel != after.channel:
        # 通知メッセージを書き込むテキストチャンネル（チャンネルIDを指定）
        botRoom = client.get_channel(777777777777777)
 
        # 退室通知
        if after.channel is None:
            await botRoom.send("**" + before.channel.name + "** から、__" + name + "__  抜けました")
            return

        # 入室通知
        if before.channel is None:
            await botRoom.send("**" + after.channel.name + "** に、__" + name + "__  参加しました")
            return

        else:
            await botRoom.send("**" + before.channel.name + "** から、__" + name + "__  抜けました")
            await botRoom.send("**" + after.channel.name + "** に、__" + name + "__  参加しました")
            
            return
            
# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)
