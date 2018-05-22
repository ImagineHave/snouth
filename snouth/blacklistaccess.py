from .db import get_db

def insert_blacklist(refresh_token):
    db = get_db()
    print(refresh_token)
    db.blacklist.insert({
        'refresh_token': refresh_token,
        })  
    
def is_refresh_token_in_blacklist(refresh_token):
    print('is refresh token in blacklist')
    db = get_db()
    query = {'refresh_token':refresh_token}
    print (refresh_token)
    blacklist_item = db.blacklist.find_one(query)
    print (blacklist_item)
    return blacklist_item
    
    