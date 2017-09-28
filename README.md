# Patrician-Bot
A Personal bot that runs on the Discord Platform.
# Running The Bot
I'd prefer if you'd just invite my bot to your server instead of trying to run your own instance but if you're convinced you want to make that happen then you need to make a bot_config.ini file with the follwing format.
``` 
[keys]
bot_token = ##############################         ;(your bot token from the discord developers page)
lastfm_key = #############################         ;(your lastfm api token from the lastfm api page)
db_key = #########################                  ;(your postgres database link)
youtube_key = ####################                  ;(your youtube database api key)

[client] ;(your other lastfm api info)
lastfm_id = #################################
lastfm_secret = #############################
lastfm_api_secret = #########################
```
# Requirements
* Python 3.5+
* Async Discord.py without voice
