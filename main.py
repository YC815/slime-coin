import discord
from dotenv import load_dotenv
import os
import sqlite3
from discord.ext import commands
import re

load_dotenv()

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)

# 建立資料庫連線
conn = sqlite3.connect('user_balances.db')
cursor = conn.cursor()

# 建立使用者餘額表格
cursor.execute('''
    CREATE TABLE IF NOT EXISTS balances (
        user_id TEXT PRIMARY KEY,
        balance INTEGER DEFAULT 0
    )
''')
conn.commit()

@bot.event
async def on_ready():
    print(f">>> {bot.user} is ready <<<")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("錢！"))

@bot.command(description="確認機器人在線狀況")
async def ping(ctx):
    await ctx.respond("Pong! 我還在線喔！")

@bot.event
async def on_message(message):
    if not message.author.bot:
        author_id = str(message.author.id)

        # 查詢使用者餘額
        cursor.execute('SELECT balance FROM balances WHERE user_id=?', (author_id,))
        result = cursor.fetchone()

        print(result)
        # 初始化使用者餘額
        if result is None:
            cursor.execute('INSERT INTO balances (user_id) VALUES (?)', (author_id,))
            conn.commit()
            balance = 0
        else:
            balance = result[0]

        # 更新使用者餘額
        balance += 5
        cursor.execute('UPDATE balances SET balance=? WHERE user_id=?', (balance, author_id))
        conn.commit()

        # 檢查訊息計數是否達到 10，給予金錢並重置計數器
        if balance >= 10:
            # 給予金錢
            await give_money(message.author, balance)
            # print("+")
            # 重置使用者餘額
            cursor.execute('UPDATE balances SET balance=0 WHERE user_id=?', (author_id,))
            conn.commit()


async def give_money(user, amount):
    
    channel = bot.get_channel(1114860808401342546)
    money_amount = amount
    await channel.send(f"{user} 獲得了 {money_amount} 元！")

@bot.command()
async def balance(ctx, user: discord.User = None):
    if user is None:
        user = ctx.author  # 若未提供 user 參數，預設為指令的執行者

    user_id = str(user.id)
    # 執行 SQL 查詢
    cursor.execute("SELECT balance FROM balances WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()  # 獲取查詢結果的第一行資料

    if result is None:
        await ctx.send("找不到該使用者的餘額資料")
    else:
        balance = result[0]  # 從結果中取得餘額
        await ctx.send(f"{user.mention} 的餘額是：{balance}")



# ----------------------- #
# 結尾
bot.run(os.getenv('TOKEN'))
cursor.close()
conn.close()
