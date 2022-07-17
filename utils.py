from tinydb import TinyDB, Query
import time
db = TinyDB('../database.json')
query = Query()

def check_for(guild_id, query, value):
  result = db.search(query.guild_id == guild_id)
  if result == []:
    db.insert({'guild_id': guild_id})
    return False
  else:
    if 'query' not in result[0]: return False
    if result[0]['query'] == value:
      return True
    
def check_for_vip(guild_id):
  result = db.search(query.guild_id == guild_id)
  
  
