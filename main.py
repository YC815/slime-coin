# 初始化
import discord
from dotenv import load_dotenv
import os
import sqlite3
from discord.ext import commands
import re
from prettytable import PrettyTable
import re
import json

load_dotenv()

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)

# 連接到資料庫
conn = sqlite3.connect('bank.db')
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, money INTEGER, count INTEGER)")

# 程式區
@bot.event
async def on_ready():
    print(f">>> {bot.user} is ready <<<")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("錢！"))

@bot.command(description="確認機器人是否在線")
async def ping(ctx):
    await ctx.respond("我還在線喔！")

@bot.command(description="幫助")
async def help(ctx):
    await ctx.respond("")
@bot.event
async def on_message(message):
    if message.author.bot == False:
        print("get message from", message.author.name)
        
        # 獲取 message.author.id
        author_id = message.author.id

        # 檢查是否存在該使用者的資料
        cursor.execute("SELECT money, count FROM users WHERE id=?", (author_id,))
        user_data = cursor.fetchone()

        if user_data is not None:
            money = user_data[0]
            count = user_data[1]

            # 更新 count 值
            count += 1
            cursor.execute("UPDATE users SET count=? WHERE id=?", (count, author_id))

            if count == 10:
                # 更新資料庫中的金錢數量
                money += 5
                cursor.execute("UPDATE users SET money=?, count=? WHERE id=?", (money, 0, author_id))
                conn.commit()
                print("已成功更新使用者金錢數量。")

        else:
            # 創建新使用者的資料表
            cursor.execute("INSERT INTO users (id, money, count) VALUES (?, ?, ?)", (author_id, 0, 1))
            conn.commit()
            print("已成功創建新使用者的資料表。")

    # await bot.process_commands(message)

@bot.event
async def on_disconnect():
    # 關閉資料庫連接和游標
    cursor.close()
    conn.close()

@commands.has_permissions(administrator=True)
@bot.command(description="顯示金錢表格")
async def see(ctx):
    # 執行查詢語句
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    # 創建表格
    table = PrettyTable()
    table.field_names = ["ID", "Money", "Count"]

    # 填充資料到表格
    for row in rows:
        table.add_row(row)

    await ctx.respond(f"```\n{table}\n```")

@bot.command(pass_context = True)
async def test(ctx):
    message = await ctx.send(embed=discord.Embed(title="Text"))
    emoji = '1️⃣' # The emoji you want the bot to react with
    await message.add_reaction(emoji) # Bot reacts with that emoji you assigned

    def check(response, user):
        return str(response.emoji) in emoji # Checks that the user has responded with the correct emoji

    response, user = await bot.wait_for("reaction_add") # Waits for the user to react with the emoji
    await ctx.send("Hi!")

@bot.command(description="查看自己的餘額")
async def mymoney(ctx, user):
    print(user)
    user = re.sub(r"<@|>", "", user)
    cursor.execute("SELECT money FROM users WHERE id=?", (user,))
    row = cursor.fetchone()
    money = re.search(r'\d+', str(row))

    await ctx.respond(content = f"<@{user}>的餘額為{money.group()}元", ephemeral = False)

@bot.command(description = "黏液咖啡廳的菜單")
async def menu(ctx):
    with open('products.json', 'r') as f:
        data = json.load(f)

    embed = discord.Embed(title='黏液咖啡聽｜MENU', color=discord.Color.blue())
    embed.add_field(name='商品名',value='', inline=True)
    embed.add_field(name='商品說明',value='', inline=True)
    embed.add_field(name='價格',value='', inline=True)
        
    for key, value in data.items():
        name = value['name']
        description = value['description']
        price = value['price']

        # embed.add_field(name='ID', value=key, inline=True)
        embed.add_field(name='', value=name, inline=True)
        embed.add_field(name='', value=description, inline=True)
        embed.add_field(name='', value=price, inline=True)

    await ctx.respond(embed=embed)
    await ctx.send("若要購買請執行指令</buy:1122439990287269999>    ")

@bot.command(description="購買商品")
async def buy(ctx):
    await ctx.respond("開發中")

bot.run(os.getenv("TOKEN"))
