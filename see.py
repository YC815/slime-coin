import sqlite3
from prettytable import PrettyTable

# 連接到資料庫
conn = sqlite3.connect('bank.db')
cursor = conn.cursor()

# 執行查詢語句
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

# 創建表格
table = PrettyTable()
table.field_names = ["使用者ID", "餘額", "字數計算"]

# 填充資料到表格
for row in rows:
    table.add_row(row)

# 顯示表格
print(table)

# 關閉資料庫連接
cursor.close()
conn.close()
