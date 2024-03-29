## Please note that the servers must be on a linux system it will not work on other operating systems!!!



# Instructions for Using the Bot:

1. You need to download Python from the official website: [Python 3.10.6](https://www.python.org/downloads/release/python-3106/) (tested on this version).

2. Open the command prompt and navigate to the folder where your script is located using the command cd (path to the folder).

3. Enter the following command in the command prompt: <pre>```pip install -r requirements.txt```</pre>

4. Now you need to open the bot.py file and replace:

TELEGRAM_BOT_TOKEN = "your Telegram bot token" # Create it [here](https://t.me/BotFather)

TELEGRAM_CHAT_ID = "your chat ID" # You can find it [here](https://t.me/myidbot)

5. Now that you have everything set up, you can start the bot by running the command:<pre>```python bot.py```</pre>

6. To begin, send the command /start to the bot, and it will guide you on what to do next.





# Description of All Buttons and commands:

## Buttons:
Setup New Worker - initiates the installation of all dependencies. Upon completion, it will notify you and ask you to launch the node using the "Launch Node" button.

Reset Containers & Images - completely removes all containers and images.

Launch Node - starts or restarts your node. Make sure to press this after setting up the worker.

Check Containers Status - shows all information about containers if they are running. If not, it will indicate that there are no running containers.

Check Images Status - performs the same action as the previous function but for images.

Restart Server - restarts your remote server (takes about a minute).

## Commands:
/addserver - accepts data in the format [ip]:[username]:[pass] [name] (optional) - adds a new server to the database (saved in the file servers.json)
/delserver - accepts data in the format [ip or name] - deletes the specified server
/menu - opens the list of added servers
/addcommand - accepts data in the format [ip] [command] - binds the /launch_binary command to the selected ip (saved in the file commands.json)

# License and...

This is the first version of my bot, and there may be errors. Please feel free to report them either on GitHub in the Issues section or on Discord - rentgg.

I am also open to suggestions for improvement. However, please note that interacting with the website cloud.io.net is currently impossible because they do not have an open API.

I grant permission for other developers to use my code for further development or modification, but please credit me as the original author.


# Change log
### 25.03.2024

+added saving servers after 1 input

### 29.03.2024
add server deletion - simple removal of servers with the command /delserver [name]

add command binding /launch_binary to each server - now you can bind startup commands to each ip with the command /addcommand [ip] [command]

add a 'check all containers' button to check all servers and all containers in the format 'name - status' - now you can check the status of all servers with one button (useful for those who have many servers)

# Future updates
add a check for duplicates when adding servers

speed up the bot's work by transferring to asyncio

add a new feature that will restart the node every day

create a compiled version of the bot for windows system

