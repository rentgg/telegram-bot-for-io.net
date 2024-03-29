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





# Description of All Buttons:

Setup New Worker - initiates the installation of all dependencies. Upon completion, it will notify you and ask you to launch the node using the "Launch Node" button.

Reset Containers & Images - completely removes all containers and images.

Launch Node - starts or restarts your node. Make sure to press this after setting up the worker.

Check Containers Status - shows all information about containers if they are running. If not, it will indicate that there are no running containers.

Check Images Status - performs the same action as the previous function but for images.

Restart Server - restarts your remote server (takes about a minute).





This is the first version of my bot, and there may be errors. Please feel free to report them either on GitHub in the Issues section or on Discord - rentgg.

I am also open to suggestions for improvement. However, please note that interacting with the website cloud.io.net is currently impossible because they do not have an open API.

I grant permission for other developers to use my code for further development or modification, but please credit me as the original author.


# Change log
### 25.03.2024

+added saving servers after 1 input

# Future updates
add server deletion

add command binding /launch_binary to each server

add a 'check all containers' button to check all servers and all containers in the format 'name - status'
