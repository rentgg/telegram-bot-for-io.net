import paramiko
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler
from telegram.error import BadRequest
import time
import socket
import json

TELEGRAM_BOT_TOKEN = 'bottoken here'
TELEGRAM_CHAT_ID = 'you chat id here'

def load_servers():
    try:
        with open('servers.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    
def save_servers():
    with open('servers.json', 'w') as f:
        json.dump(servers, f)

servers = []
servers = load_servers()

def send_telegram_message(chat_id, message):
    requests.post(f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage',
                  data={'chat_id': chat_id, 'text': message})
                  
def execute_command_on_server(ip, username, password, command):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)

        stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)

        response = stdout.read().decode("utf-8")
        error = stderr.read().decode("utf-8")

        ssh.close()

        if error:
            return f"Error: {error}"
        else:
            return response
    except Exception as e:
        return str(e)
    
def execute_command_on_server1(ip, username, password, command):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)

        stdin, stdout, stderr = ssh.exec_command(command)

        time.sleep(60)

        ssh.close()
        
        return "Script installation successful."
    except Exception as e:
        return str(e)
        
def check_all_servers(update, context):
    chat_id = update.message.chat_id
    if str(chat_id) == TELEGRAM_CHAT_ID:

        if not servers:
            send_telegram_message(chat_id, "No servers added. Please add a server first.")
            return

        send_telegram_message(chat_id, "Checking all servers...")
        results = []

        for server in servers:
            ip = server['ip']
            username = server['username']
            password = server['password']
            servername = server['name']

            if authenticate_server(ip, username, password):
                results.append(f"{servername} - Online")
            else:
                results.append(f"{servername} - Offline")

        message = "\n".join(results)
        send_telegram_message(chat_id, message)
    else:
        update.message.reply_text("Sorry, you are not authorized.")
        

def is_valid_server(ip, username, password):
    try:
        with paramiko.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=username, password=password, timeout=5)
            return True
    except (paramiko.AuthenticationException, socket.timeout) as e:
        print("Error checking server validity:", e)
        return False
    except Exception as e:
        print("An error occurred while checking server validity:", e)
        return False

def authenticate_server(ip, username, password):
    try:
        with paramiko.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=username, password=password, timeout=5)
            return True
    except paramiko.AuthenticationException as e:
        print("Error authenticating server:", e)
        return False
    except socket.timeout as e:
        print("Connection timeout:", e)
        return False
    except Exception as e:
        print("An error occurred while authenticating server:", e)
        return False
        paramiko.SSHClient().load_system_host_keys()
        paramiko.SSHClient().clear_all_host_keys()

def add_server(update, context):
    chat_id = update.message.chat_id
    if str(chat_id) == TELEGRAM_CHAT_ID:
        text = update.message.text
        data = text.split(' ', 1)[-1]

        context.user_data['state'] = STATE_MAIN_MENU

        if not data:
            send_telegram_message(chat_id, "Please provide server details in the format 'ip:user:password [servername]'.")
            return

        server_info = data.split(' ')
        
        if len(server_info) == 2:
            ip_userpass, servername = server_info
            if ':' in ip_userpass:
                ip, userpass = ip_userpass.split(':', 1)
                if ':' in userpass:
                    username, password = userpass.split(':', 1)
                else:
                    send_telegram_message(chat_id, "Invalid format. Please use 'ip:user:password [servername]'.")
                    return
            else:
                send_telegram_message(chat_id, "Invalid format. Please use 'ip:user:password [servername]'.")
                return
        elif len(server_info) == 1:
            ip_userpass = server_info[0]
            if ':' in ip_userpass:
                ip, userpass = ip_userpass.split(':', 1)
                if ':' in userpass:
                    username, password = userpass.split(':', 1)
                    servername = ip.replace(".", "_")
                else:
                    send_telegram_message(chat_id, "Invalid format. Please use 'ip:user:password [servername]'.")
                    return
            else:
                send_telegram_message(chat_id, "Invalid format. Please use 'ip:user:password [servername]'.")
                return
        else:
            send_telegram_message(chat_id, "Invalid format. Please use 'ip:user:password [servername]'.")
            return

        servername = servername.replace("_", ".")

        send_telegram_message(chat_id, "Checking server validity...")
        if not is_valid_server(ip, username, password):
            send_telegram_message(chat_id, "Invalid server. Please check the provided details.")
            return

        send_telegram_message(chat_id, "Authenticating server...")
        if not authenticate_server(ip, username, password):
            send_telegram_message(chat_id, "Server authentication failed. Please check the provided credentials.")
            return

        servers.append({'name': servername, 'ip': ip, 'username': username, 'password': password})
        save_servers()
        send_telegram_message(chat_id, f"Server {servername} added successfully. Now you can use /menu")
    else:
        update.message.reply_text("Sorry, you are not authorized.")


def show_menu(update, context):
    allowed_chat_id = TELEGRAM_CHAT_ID

    chat_id = update.effective_chat.id

    if str(chat_id) == str(allowed_chat_id):

        if not servers:
            send_telegram_message(chat_id, "No servers added. Please add a server first.")
            return

        buttons = []
        for server in servers:
            server_name = server['name']
            ip = server['ip']
            if not server_name:
                server_name = ip
            button = InlineKeyboardButton(server_name, callback_data=ip)
            buttons.append([button])

        buttons.append([InlineKeyboardButton("Check Servers", callback_data="/checkservers")])

        reply_markup = InlineKeyboardMarkup(buttons)

        if update.message:
            update.message.reply_text('Please select a server or choose an action:', reply_markup=reply_markup)
        elif update.callback_query and update.callback_query.message:
            update.callback_query.message.reply_text('Please select a server or choose an action:', reply_markup=reply_markup)
    else:
        update.message.reply_text("Sorry, you are not authorized.")
    
STATE_MAIN_MENU = 1

def start_main_menu(update, context):
    allowed_chat_id = TELEGRAM_CHAT_ID

    chat_id = update.effective_chat.id

    if str(chat_id) == str(allowed_chat_id):
        show_menu(update, context)
        return STATE_MAIN_MENU
    else:
        update.message.reply_text("Sorry, you are not authorized.")
   
def server_button_click(update, context):
        query = update.callback_query
        ip = query.data

        keyboard = [
            [InlineKeyboardButton("Setup New Worker", callback_data=f"setup_{ip}")],
            [InlineKeyboardButton("Launch Node / Restart", callback_data=f"launch_{ip}")],
            [InlineKeyboardButton("Reset Containers & Images", callback_data=f"reset_{ip}")],
            [InlineKeyboardButton("Check Containers Status", callback_data=f"status_{ip}")],
            [InlineKeyboardButton("Check Images Status", callback_data=f"statusimage_{ip}")],
            [InlineKeyboardButton("Restart Server", callback_data=f"restart_{ip}")],
            [InlineKeyboardButton("Back to Servers", callback_data="/menu")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

        query.message.reply_text("Please select an action:", reply_markup=reply_markup)

        context.user_data['state'] = STATE_MAIN_MENU

def server_menu_click(update, context):
        query = update.callback_query
        data = query.data.split('_')
        action = data[0]

        if len(data) > 1:
            ip = data[1]
        else:
            ip = None

        if action == "reset":
            if ip is not None:
                command_stop = "docker stop $(docker ps -qa)"
                command_rm_containers = "docker rm $(docker ps -qa)"
                command_rm_images = "docker rmi -f $(docker images -qa)"
                server = next((server for server in servers if server['ip'] == ip), None)
                if server:
                    username = server['username']
                    password = server['password']
                    try:
                        send_telegram_message(query.message.chat_id, "Stopping containers...")
                        response_stop = execute_command_on_server(ip, username, password, command_stop)
                        if response_stop:
                            stopped_containers = [name for name in response_stop.split('\n') if name]
                            stopped_containers_str = ' '.join(stopped_containers)
                            send_telegram_message(query.message.chat_id, f"Containers {stopped_containers_str} were successfully stopped.")

                        send_telegram_message(query.message.chat_id, "Removing containers...")
                        response_rm_containers = execute_command_on_server(ip, username, password, command_rm_containers)
                        if response_rm_containers:
                            send_telegram_message(query.message.chat_id, "Containers removed successfully.")

                        send_telegram_message(query.message.chat_id, "Removing images...")
                        response_rm_images = execute_command_on_server(ip, username, password, command_rm_images)
                        if response_rm_images:
                            send_telegram_message(query.message.chat_id, "Images removed successfully.")

                        send_telegram_message(query.message.chat_id, "Container and image reset successful. To launch a clean setup, press 'Launch Node'.")

                    except Exception as e:
                        send_telegram_message(query.message.chat_id, f"Failed to connect to server: {e}")
                else:
                    send_telegram_message(query.message.chat_id, "Server details not found.")
            else:
                send_telegram_message(query.message.chat_id, "Invalid action.")

        if action == "launch":
            if ip is not None:
                send_telegram_message(query.message.chat_id, "Enter the command to start your Worker, which should begin with ./launch_binary_linux")

                context.user_data['ip'] = ip
                return AWAITING_LAUNCH_COMMAND

            else:
                send_telegram_message(query.message.chat_id, "Invalid action.")

        elif action == "status":
            if ip is not None:
                command = "docker ps"
                server = next((server for server in servers if server['ip'] == ip), None)
                if server:
                    username = server['username']
                    password = server['password']
                    try:
                        containers_status = execute_command_on_server(ip, username, password, command)
                        formatted_output = format_containers_status(containers_status)
                        if formatted_output:
                            send_telegram_message(query.message.chat_id, f"Containers status on server {ip}:\n{formatted_output}")
                        else:
                            send_telegram_message(query.message.chat_id, f"No active containers found on server {ip}.")
                    except Exception as e:
                        send_telegram_message(query.message.chat_id, f"Failed to connect to server: {e}")
                else:
                    send_telegram_message(query.message.chat_id, "Server details not found.")
            else:
                send_telegram_message(query.message.chat_id, "Invalid action.")

        elif action == "statusimage":
            if ip is not None:
                command = "docker images -a"
                server = next((server for server in servers if server['ip'] == ip), None)
                if server:
                    username = server['username']
                    password = server['password']
                    try:
                        img_status = execute_command_on_server(ip, username, password, command)
                        formatted_output = format_img_status(img_status)
                        if formatted_output:
                            send_telegram_message(query.message.chat_id, f"Images status on server {ip}:\n{formatted_output}")
                        else:
                            send_telegram_message(query.message.chat_id, f"No active Images found on server {ip}.")
                    except Exception as e:
                        send_telegram_message(query.message.chat_id, f"Failed to connect to server: {e}")
                else:
                    send_telegram_message(query.message.chat_id, "Server details not found.")
            else:
                send_telegram_message(query.message.chat_id, "Invalid action.")

        if action == "setup":
            if ip is not None:
                server = next((server for server in servers if server['ip'] == ip), None)
                if server:
                    username = server['username']
                    password = server['password']
                    try:
                            send_telegram_message(query.message.chat_id, "Downloading necessary files...")
                            download_command = "curl -L https://github.com/ionet-official/io-net-official-setup-script/raw/main/ionet-setup.sh -o ionet-setup.sh"
                            execute_command_on_server(ip, username, password, download_command)
                            send_telegram_message(query.message.chat_id, "The installation file has been successfully downloaded.")

                            send_telegram_message(query.message.chat_id, "Granting permissions for installation...")
                            setup_command = "chmod +x ionet-setup.sh"
                            execute_command_on_server(ip, username, password, setup_command)
                            send_telegram_message(query.message.chat_id, "Permissions for installation have been granted")
                            setup2_command = "/root/ionet-setup.sh"
                            send_telegram_message(query.message.chat_id, "Installing dependencies. This may take about 1 minute.")
                            execute_command_on_server1(ip, username, password, setup2_command)

                            send_telegram_message(query.message.chat_id, "Installing worker file...")
                            download_worker_command = "curl -L https://github.com/ionet-official/io_launch_binaries/raw/main/launch_binary_linux -o launch_binary_linux"
                            execute_command_on_server(ip, username, password, download_worker_command)

                            send_telegram_message(query.message.chat_id, "Granting permissions to execute the file..")
                            chmod_command = "chmod +x launch_binary_linux"
                            execute_command_on_server(ip, username, password, chmod_command)
                            send_telegram_message(query.message.chat_id, "Permissions to execute the file have been granted.")

                            time.sleep (2)

                            send_telegram_message(query.message.chat_id, "New worker successfully created. You can launch it by pressing the 'Launch Node' button")
                            
                    except Exception as e:
                        send_telegram_message(query.message.chat_id, f"Failed to setup new worker: {e}")
                else:
                    send_telegram_message(query.message.chat_id, "Server details not found.")
            else:
                send_telegram_message(query.message.chat_id, "Invalid action.")

        elif action == "restart":
            if ip is not None:
                command = "reboot"
                server = next((server for server in servers if server['ip'] == ip), None)
                if server:
                    username = server['username']
                    password = server['password']
                    try:
                        execute_command_on_server(ip, username, password, command)
                        send_telegram_message(query.message.chat_id, f"Restarting Server... {ip}")
                    except Exception as e:
                        send_telegram_message(query.message.chat_id, f"Failed to connect to server: {e}")
                else:
                    send_telegram_message(query.message.chat_id, "Server details not found.")
            else:
                send_telegram_message(query.message.chat_id, "Invalid action.")

        try:
            context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        except BadRequest as e:
            print("Error deleting message:", e)

        if action == "/checkservers":
            check_all_servers(update, context)
        else:
            if 'state' in context.user_data and context.user_data['state'] == STATE_MAIN_MENU:
                start_main_menu(update, context)

def get_launch_command(update, context):
    chat_id = update.message.chat_id
    if str(chat_id) == TELEGRAM_CHAT_ID:
        command = update.message.text
        ip = context.user_data.get('ip')
        if not command.startswith("./launch_binary_linux"):
            send_telegram_message(update.message.chat_id, "Incorrect command...")
            return AWAITING_LAUNCH_COMMAND

        expected_command_format = "./launch_binary_linux --device_id=UUID --user_id=UUID --operating_system='OS' --usegpus=false --device_name=NAME"
        if not validate_command_format(command, expected_command_format):
            error_message = "Invalid command format. Please use the following format:\n\n"
            error_message += expected_command_format
            send_telegram_message(update.message.chat_id, error_message)
            return AWAITING_LAUNCH_COMMAND

        if ip is not None:
            server = next((server for server in servers if server['ip'] == ip), None)
            if server:
                username = server['username']
                password = server['password']
                try:
                    execute_command_on_server(ip, username, password, command)
                    send_telegram_message(update.message.chat_id, "Node has been successfully launched. /menu")
                except Exception as e:
                    send_telegram_message(update.message.chat_id, f"Failed to connect to server: {e}")
            else:
                send_telegram_message(update.message.chat_id, "Server details not found.")
        else:
            send_telegram_message(update.message.chat_id, "Invalid action.")

        return ConversationHandler.END
    else:
        update.message.reply_text("Sorry, you are not authorized.")

def validate_command_format(command, expected_format):
    expected_parts = expected_format.split(" ")

    command_parts = command.split(" ")

    if len(expected_parts) != len(command_parts):
        return False

    for expected, actual in zip(expected_parts, command_parts):
        if expected.startswith("--") and actual.startswith("--"):
            continue
        elif expected == actual:
            continue
        else:
            return False

    return True
        
def format_containers_status(containers_status):
    lines = containers_status.strip().split('\n')

    lines = lines[1:]

    formatted_output = []

    for line in lines:
        parts = line.split()

        container_id = parts[0]
        image = parts[1]
        created = " ".join(parts[5:8])
        ports = " ".join(parts[11:12])

        container_info = (
            f"📦 CONTAINER ID: {container_id}\n"
            f"🖼️ IMAGE: {image}\n"
            f"🏷️ NAMES: {ports}\n"
            f"🕰️ CREATED: {created}\n"
            f"⚠️ STATUS: Running\n"
        )

        formatted_output.append(container_info)

    result = "\n\n".join(formatted_output)

    return result

def format_img_status(img_status):
    lines = img_status.strip().split('\n')

    lines = lines[1:]

    formatted_output1 = []

    for line in lines:
        parts = line.split()

        container_id = parts[0]
        image = parts[1]
        command = parts[2]
        created = " ".join(parts[3:6])
        status = " ".join(parts[6:11])

        img_info = (
            f"📦 REPOSITORY: {container_id}\n"
            f"📦 TAG: {image}\n"
            f"🖼️ IMAGE ID: {command}\n"
            f"🕰️ CREATED: {created}\n"
            f"⚠️ SIZE: {status}\n"
        )

        formatted_output1.append(img_info)

    result = "\n\n".join(formatted_output1)

    return result
    
def check_all_servers(update, context):
    allowed_chat_id = TELEGRAM_CHAT_ID

    chat_id = update.effective_chat.id

    if str(chat_id) == str(allowed_chat_id):
        if not servers:
            send_telegram_message(chat_id, "No servers added. Please add a server first.")
            return

        send_telegram_message(chat_id, "Checking all servers...")
        results = []

        for server in servers:
            ip = server['ip']
            username = server['username']
            password = server['password']
            servername = server['name']

            masked_password = '*' * len(password)

            status = "Online" if authenticate_server(ip, username, password) else "Offline"
            results.append(f"Server: {servername}\nStatus: {status}\nIP: {ip}\nUsername: {username}\nPassword: {masked_password}\n")

        message = "\n".join(results)
        send_telegram_message(chat_id, message)
    else:
        update.message.reply_text("Sorry, you are not authorized.")


AWAITING_LAUNCH_COMMAND = 1

launch_command_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.text & ~Filters.command, get_launch_command)],
    states={
        AWAITING_LAUNCH_COMMAND: [MessageHandler(Filters.text & ~Filters.command, get_launch_command)]
    },
    fallbacks=[]
)


def start(update, context):
    chat_id = TELEGRAM_CHAT_ID
    if str(chat_id) == TELEGRAM_CHAT_ID:
        update.message.reply_text(
        "Hello! I'm a bot for managing servers and their workers.\n"
        "I accept the following commands:\n\n"
        "/addserver ip:user:pass (name) - adds a new server and checks its availability.\n"
        "/menu - displays a list of all active servers.\n\n"
        "To add a new server, use the /addserver command with IP, username, password, and optionally a server name in parentheses.\n"
        "For example: /addserver 123.45.67.89:user123:pass123 (MyServer)\n"
        "To view the server menu, press /menu.")
    else:
        update.message.reply_text("Sorry, you are not authorized.")

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("addserver", add_server))
    dp.add_handler(CommandHandler("menu", show_menu))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(server_button_click, pattern='^([0-9]{1,3}\.){3}[0-9]{1,3}$'))
    dp.add_handler(CallbackQueryHandler(server_menu_click, pattern='^setup_'))
    dp.add_handler(CallbackQueryHandler(server_menu_click, pattern='^reset_'))
    dp.add_handler(CallbackQueryHandler(server_menu_click, pattern='^launch_'))
    dp.add_handler(CallbackQueryHandler(server_menu_click, pattern='^status_'))
    dp.add_handler(CallbackQueryHandler(server_menu_click, pattern='^statusimage_'))
    dp.add_handler(CallbackQueryHandler(server_menu_click, pattern='^restart_'))
    dp.add_handler(CallbackQueryHandler(server_menu_click, pattern='^/menu'))
    dp.add_handler(CallbackQueryHandler(server_menu_click, pattern='^'))   
    dp.add_handler(CommandHandler("checkservers", check_all_servers))
    dp.add_handler(launch_command_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
        main()
