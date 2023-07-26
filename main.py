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
from discord.ui import Select, View

load_dotenv()

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)

# 連接到資料庫
# conn = sqlite3.connect("bank.db")
# cursor = conn.cursor()
# cursor.execute(
#     "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, money INTEGER, count INTEGER)"
# )


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
    await ctx.respond("# 指令列表\n1. 獲得幫助 </help:1122427294108094484>\n2. 查詢使用者餘額 </mymoney:1122431607748448396>\n3. 查看餘額總覽表 </see:1122425032073826344>\n4. 查看商品清單 </menu:1122439329873133599>\n5. 買東西 </buy:1122439990287269999>\n6. 匯款 </pay:1122489485763031160>")


@bot.event
async def on_message(message):
    if message.author.bot == False:
        conn = sqlite3.connect("bank.db")
        cursor = conn.cursor()
        cursor.execute(
           "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, money INTEGER, count INTEGER)"
        )
        # print(message.content)
        # print("get message from", message.author.name)

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

            if count >= 30:
                # 更新資料庫中的金錢數量
                money += 5
                cursor.execute(
                    "UPDATE users SET money=?, count=? WHERE id=?",
                    (money, 0, author_id),
                )
                conn.commit()
                print("已成功更新使用者金錢數量。")

        else:
            # 創建新使用者的資料表
            cursor.execute(
                "INSERT INTO users (id, money, count) VALUES (?, ?, ?)",
                (author_id, 0, len(message.content)),
            )
            conn.commit()
            print("已成功創建新使用者的資料表。")
        # 關閉資料庫連接
        cursor.close()
        conn.close()
    # await bot.process_commands(message)

# @commands.has_permissions(administrator=True)
@bot.command(description="顯示金錢表格")
async def see(ctx):
    conn = sqlite3.connect("bank.db")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, money INTEGER, count INTEGER)"
    )
    # 執行查詢語句
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    # 創建表格
    table = PrettyTable()
    table.field_names = ["User ID", "balance", "word count"]

    # 填充資料到表格
    for row in rows:
        table.add_row(row)

    await ctx.respond(f"```\n{table}\n```")
    # 關閉資料庫連接
    cursor.close()
    conn.close()


@bot.command(description="查看自己的餘額")
async def mymoney(ctx, user):
    conn = sqlite3.connect("bank.db")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, money INTEGER, count INTEGER)"
    )
    print(user)
    user = re.sub(r"<@|>", "", user)
    cursor.execute("SELECT money FROM users WHERE id=?", (user,))
    row = cursor.fetchone()
    money = re.search(r"\d+", str(row))

    await ctx.respond(content=f"<@{user}>的餘額為{money.group()}元", ephemeral=False)


@bot.command(description="黏液咖啡廳的菜單")
async def menu(ctx):
    with open("products.json", "r") as f:
        data = json.load(f)

    embed = discord.Embed(title="黏液咖啡聽｜MENU", color=discord.Color.blue())
    embed.add_field(name="商品名", value="", inline=True)
    embed.add_field(name="商品說明", value="", inline=True)
    embed.add_field(name="價格", value="", inline=True)
    for key, value in data.items():
        name = value["name"]
        description = value["description"]
        price = value["price"]

        # embed.add_field(name='ID', value=key, inline=True)
        embed.add_field(name="", value=name, inline=True)
        embed.add_field(name="", value=description, inline=True)
        embed.add_field(name="", value=price, inline=True)

    await ctx.respond(embed=embed)
    await ctx.send("若要購買請執行指令</buy:1122439990287269999>    ")


@bot.command(description="購買商品")
async def buy(ctx):
    conn = sqlite3.connect("bank.db")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, money INTEGER, count INTEGER)"
    )
    user_id = ctx.author.id
    print(user_id)
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user_data = cursor.fetchone()
    current_money = user_data[1]
    if current_money <= 0:
        await ctx.respond("餘額不足")
        return
    select = Select(options=[], placeholder="選擇一個商品")
    with open("products.json", "r") as f:
        data = json.load(f)
    
    for key, value in data.items():
        select.add_option(label=str(value["name"]), emoji=str(value["emoji"]), description=str(value["description"]) + " " + str(value["price"]) + "元")
    view = View()
    view.add_item(select)
    async def my_callback(interaction):
        if select.values[0] == "熱情招呼":
            await interaction.response.send_message(f"早安{'!'*100}")
            new_money = current_money - 5
            cursor.execute("UPDATE users SET money=? WHERE id=?", (new_money, user_id))
            conn.commit()
            cursor.close()
            conn.close()

    select.callback = my_callback
    await ctx.respond(view=view)
    print(ctx)


@bot.command(description="匯款")
async def pay(ctx, user, money):
    conn = sqlite3.connect("bank.db")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, money INTEGER, count INTEGER)"
    )
    # 獲取執行指令的使用者ID
    sender_id = ctx.author.id
    
    # 取得目標使用者ID
    user_id = re.sub(r"<@|>", "", user)

    # 檢查輸入的金錢是否為有效數字
    try:
        money = int(money)
        if money <= 0:
            await ctx.respond(f"{money}不是一個有效的數字。")
            return
    except ValueError:
        await ctx.respond("請輸入有效的金錢數字。")
        return

    # 獲取執行指令使用者的餘額
    cursor.execute("SELECT money FROM users WHERE id=?", (sender_id,))
    sender_balance = cursor.fetchone()

    if sender_balance is None:
        await ctx.respond("找不到執行指令的使用者資料。")
        return

    sender_balance = int(sender_balance[0])

    # 檢查執行指令使用者的餘額是否足夠
    if sender_balance < money:
        await ctx.respond("餘額不足，無法進行匯款。")
        return

    # 執行匯款操作
    try:
        # 更新執行指令使用者的餘額
        sender_balance -= money
        cursor.execute("UPDATE users SET money=? WHERE id=?", (sender_balance, sender_id))

        # 更新目標使用者的餘額
        cursor.execute("SELECT money FROM users WHERE id=?", (user_id,))
        user_balance = cursor.fetchone()

        if user_balance is None:
            # 若目標使用者資料不存在，創建新資料
            cursor.execute("INSERT INTO users (id, money, count) VALUES (?, ?, ?)", (user_id, money, 1))
        else:
            # 目標使用者資料已存在，增加餘額
            user_balance = int(user_balance[0])
            user_balance += money
            cursor.execute("UPDATE users SET money=? WHERE id=?", (user_balance, user_id))

        # 提交資料庫變更
        conn.commit()

        await ctx.respond("匯款成功！")
    except Exception as e:
        await ctx.respond("匯款失敗，請稍後再試。")
        print(str(e))
    # 關閉資料庫連接
    cursor.close()
    conn.close()

@commands.has_permissions(administrator=True)
@bot.command()
async def set(ctx, user, money):
    conn = sqlite3.connect("bank.db")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, money INTEGER, count INTEGER)"
    )
    # 獲取目標使用者ID
    user_id = re.sub(r"<@|>", "", user)

    # 檢查輸入的金錢是否為有效數字
    try:
        money = int(money)
    except ValueError:
        await ctx.respond("請輸入有效的金錢數字。")
        return

    # 檢查目標使用者是否存在於資料庫
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user_data = cursor.fetchone()

    if user_data is None:
        # 若目標使用者資料不存在，創建新資料
        cursor.execute("INSERT INTO users (id, money, count) VALUES (?, ?, ?)", (user_id, money, 1))
    else:
        # 目標使用者資料已存在，更新餘額
        cursor.execute("UPDATE users SET money=? WHERE id=?", (money, user_id))

    # 提交資料庫變更
    conn.commit()

    await ctx.respond(f"已成功設定使用者 <@{user_id}> 的餘額為 {money} 元。")
    # 關閉資料庫連接
    cursor.close()
    conn.close()

@commands.has_permissions(administrator=True)
@bot.command(description="增加使用者餘額")
async def add(ctx, user, money):
    conn = sqlite3.connect("bank.db")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, money INTEGER, count INTEGER)"
    )
    # 獲取執行指令的使用者ID
    sender_id = ctx.author.id

    # 獲取目標使用者ID
    user_id = re.sub(r"<@|>", "", user)

    # 檢查輸入的金錢是否為有效數字
    try:
        money = int(money)
    except ValueError:
        await ctx.respond("請輸入有效的金錢數字。")
        return

    # 檢查目標使用者是否存在於資料庫
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user_data = cursor.fetchone()

    if user_data is None:
        # 若目標使用者資料不存在，創建新資料
        cursor.execute("INSERT INTO users (id, money, count) VALUES (?, ?, ?)", (user_id, money, 1))
    else:
        # 目標使用者資料已存在，更新餘額
        current_money = user_data[1]
        new_money = current_money + money
        cursor.execute("UPDATE users SET money=? WHERE id=?", (new_money, user_id))

    # 提交資料庫變更
    conn.commit()

    await ctx.respond(f"已成功增加使用者 <@{user_id}> 的餘額 {money} 元。")
    # 關閉資料庫連接
    cursor.close()
    conn.close()


@commands.has_permissions(administrator=True)
@bot.command(description="減少使用者餘額")
async def minus(ctx, user, money):
    conn = sqlite3.connect("bank.db")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, money INTEGER, count INTEGER)"
    )
    # 獲取執行指令的使用者ID
    sender_id = ctx.author.id

    # 獲取目標使用者ID
    user_id = re.sub(r"<@|>", "", user)

    # 檢查輸入的金錢是否為有效數字
    try:
        money = int(money)
    except ValueError:
        await ctx.respond("請輸入有效的金錢數字。")
        return

    # 檢查目標使用者是否存在於資料庫
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user_data = cursor.fetchone()

    if user_data is None:
        await ctx.respond("該使用者不存在於資料庫中。")
        return

    current_money = user_data[1]

    if current_money < money:
        await ctx.respond("使用者餘額不足，無法進行扣款。")
        return

    new_money = current_money - money
    cursor.execute("UPDATE users SET money=? WHERE id=?", (new_money, user_id))

    # 提交資料庫變更
    conn.commit()

    await ctx.respond(f"已成功減少使用者 <@{user_id}> 的餘額 {money} 元。")
    # 關閉資料庫連接
    cursor.close()
    conn.close()


bot.run(os.getenv("TOKEN"))
