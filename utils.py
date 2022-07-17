import sqlite3
import time

db = sqlite3.connect('../grouchy.db')
cur = db.cursor()
    
def check_for_vip(guild_id):
  for row in cur.execute('SELECT * FROM guilds WHERE id=?',(guild_id,)):
    return row[1]
  cur.execute("INSERT INTO guilds VALUES (?,0)",(guild_id,))
  db.commit()
  return 0
