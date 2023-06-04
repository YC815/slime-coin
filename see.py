import sqlite3
from prettytable import PrettyTable

# 建立資料庫連線
conn = sqlite3.connect('user_balances.db')
cursor = conn.cursor()

# 執行 SQL 查詢
cursor.execute('SELECT * FROM balances')
results = cursor.fetchall()

# 建立表格
table = PrettyTable()
table.field_names = ['User ID', 'Balance']

# 加入資料到表格
for result in results:
    table.add_row(result)

# 顯示表格
print(table)

# 關閉資料庫連線
cursor.close()
conn.close()
