# Patrician-Bot
A Personal bot that runs on the Discord Platform.

# Commands And Uses


_**General Commands**_

*Youtube integration*: Fetch videos from youtube by passing your search term.
![yt](https://i.imgur.com/BZG27Zt.png)

*Disabling Commands*: Disable and enable commands in a channel.
![commands](https://i.imgur.com/eDRuez7.png)

*Quoting Messages*: Quote memorable chat messages.
![quote](https://i.imgur.com/7747Rdn.png)

*Guessing Game*: Guess the artist behind the lyrics.
![lyrics](https://i.imgur.com/CFUHzhv.png)

_**Collages And Charts**_

Get a collage of your most listened albums of the week 

![collage1](https://i.imgur.com/NDYKxGy.png)

Store a chart of your favorite albums , get other's charts and also find out what they're listening to.
![fm](https://i.imgur.com/71wxNvj.png)
![collage](https://i.imgur.com/PJSeRs0.png)


# Running The Bot
I'd prefer if you'd just invite my bot to your server [(using this link)](https://www.discordapp.com/oauth2/authorize?&client_id=280080975617196032&scope=bot&permissions=0) instead of trying to run your own instance but if you're convinced you want to make that happen then you need to make a bot_config.ini file with the following format.
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
