import sqlite3
conn = sqlite3.connect('C:\\Users\\lenovo\\Desktop\\VS\\EquipShare\\equipshare.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(cur.fetchall())
