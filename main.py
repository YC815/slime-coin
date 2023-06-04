import discord
from dotenv import load_dotenv
import os
import sqlite3
from discord.ext import commands

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

# 開機
@bot.event
async def on_ready():
    print(f">>> {bot.user} is ready <<<")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("錢！"))

# Ping
@bot.command(description="確認機器人在線狀況")
async def ping(ctx):
    await ctx.respond("Pong! 我還在線喔！")

# 說話賺錢
@bot.event
async def on_message(message):
    if not message.author.bot:
        author_id = str(message.author.id)

        # 查詢使用者餘額
        cursor.execute('SELECT balance FROM balances WHERE user_id=?', (author_id,))
        result = cursor.fetchone()

        # 初始化使用者餘額
        if result is None:
            cursor.execute('INSERT INTO balances (user_id) VALUES (?)', (author_id,))
            conn.commit()
            balance = 0
        else:
            balance = result[0]

        # 更新使用者餘額
        balance += 1
        cursor.execute('UPDATE balances SET balance=? WHERE user_id=?', (balance, author_id))
        conn.commit()

        # 檢查訊息計數是否達到 10，給予金錢並重置計數器
        if balance >= 10:
            # 給予金錢
            await give_money(message.author, balance)

            # 重置使用者餘額
            cursor.execute('UPDATE balances SET balance=0 WHERE user_id=?', (author_id,))
            conn.commit()

    await bot.process_commands(message)


# # 給錢
# @commands.has_permissions(administrator=True)
# @bot.command(description="給使用者黏幣")
# async def give_money(user, amount):
#     print(user)
#     cursor.execute('UPDATE balances SET balance=? WHERE user_id=?', (amount, user))
#     conn.commit()
#     await user.send(f"你獲得了 {amount} 元！")


bot.run(os.getenv('TOKEN'))

# 關閉資料庫連線
cursor.close()
conn.close()
