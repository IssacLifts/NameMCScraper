
class Config:
    with open('../config.txt') as config:
        cookie_text = config.readlines()
        
    COOKIE = cookie_text[0]
    