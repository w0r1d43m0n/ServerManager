import os
import shutil
from datetime import datetime
import uuid

originalCWD = os.getcwd()

if not os.path.exists('servermgr.ini'):
    print("Welcome to ServerManager")
    serverPath = input("Where should ServerManager look for servers (full path)?: ")
    with open('servermgr.ini', 'w+') as ini:
        ini.write(serverPath)
    os.system('cls')
    print("ServerManager v0.1-Pre_Release for Windows")
else:
    with open('servermgr.ini', 'r') as ini:
        lines = ini.readlines()
        serverPath = lines[0]
    print("ServerManager v0.1-Pre_Release for Windows")

try:
    servers = next(os.walk(serverPath))[1]
except:
    print("Server path does not exist!")
    os.remove("servermgr.ini")
    print("ServerManager reset. Quitting...")
    exit()

print("Type \"help\" for a list of commands")
while True:
    try:
        cmd = input("> ")
    except KeyboardInterrupt:
        print("exit")
        print("Quitting.")
        exit()

    if cmd.lower() == "reset":
        os.remove("servermgr.ini")
        print("ServerManager reset")
        exit()

    elif cmd.lower() == "exit":
        print("Quitting.")
        exit()

    elif cmd.lower() in ["clear", "cls"]:
        os.system("cls")
        print("ServerManager v1.0.0 on Windows x86_64")
        print("Type \"help\" for a list of commands")
        continue

    elif cmd.lower().startswith("info "):
        cmd = cmd.split(' ')
        if len(cmd) != 2:
            print("Malformed command, type \"help\" for help")
            continue
        if cmd[1] == "servers":
            for server in servers:
                print(f"Server {server}")
                if os.path.exists(os.path.join(serverPath, server, "start.bat")):
                    print(f"Folder {server} does contain a Minecraft Server!")
                else:
                    print(f"Folder {server} does NOT contain a compatible Minecraft Server.")
        elif cmd[1] == "config":
            with open("servermgr.ini", 'r') as ini:
                lines = ini.readlines()
                print(f"Searching for servers at \"{lines[0]}\"")
        else:
            print("Malformed command, type \"help\" for help")
    
    elif cmd.lower().startswith("start "):
        cmd = cmd.split(' ')
        if len(cmd) != 2:
            print("Malformed command, type \"help\" for help")
            continue
        if cmd[1] in servers:
            print(f"Starting server \"{cmd[1]}\".")
            os.chdir(os.path.join(serverPath, cmd[1])) # This means we can't access the config anymore.
            try:
                os.system("start.bat")
            except KeyboardInterrupt:
                pass
            os.chdir(originalCWD)
        else:
            print(f"Server \"{cmd[1]}\" doesn't exist. Are you sure you typed it correctly?")  
        
        continue
    
    elif cmd.lower().startswith("backup "):
        cmd = cmd.split(' ')
        if len(cmd) != 2:
            print("Malformed command, type \"help\" for help")
            continue
        if cmd[1] in servers:
            print(f"Starting backup of server \"{cmd[1]}\".")
            os.chdir(os.path.join(serverPath, cmd[1])) # Can we access it now? (Nope)
            if not os.path.exists("SMBackup"):
                print("Folder \"SMBackup\" does not exist. Creating it.")
                os.mkdir("SMBackup")

            backupFolder = os.path.join("SMBackup", datetime.now().strftime("%I.%M %p %m.%d.%Y"))

            print("Starting backup. (This may take a while on large servers!)")
            try:
                shutil.copytree(".", backupFolder, ignore=shutil.ignore_patterns("Backup", "SMBackup"))
            except Exception as e:
                print("Fatal error! Couldn't back up server")
                print(f"Technical Details:\n{e}")
                print("Reverting changes.")
                try:
                    shutil.rmtree(backupFolder)
                except Exception as e:
                    print("Couldn't revert changes!!")
                    print("Technical Details:\n{e}")
                continue

            print(f"Backup completed to {backupFolder}")
            
            os.chdir(originalCWD)
        else:
            print(f"Server \"{cmd[1]}\" doesn't exist. Are you sure you typed it correctly?")  
            print("Backup aborted")
            continue

        continue

    elif cmd.lower().startswith("rollback "):
        cmd = cmd.split(' ', 2)
        if len(cmd) != 3:
            print("Malformed command, type \"help\" for help")
            continue
        
        if cmd[1] in servers:
            if cmd[2].strip() == "":
                print("Malformed command, type \"help\" for help")
                continue

            os.chdir(os.path.join(serverPath, cmd[1])) # No, you still can't access the config!
            if not os.path.exists("SMBackup"):
                print("SMBackup folder does not exist! Can't restore backup")
                continue
            
            if not os.path.exists(os.path.join("SMBackup", cmd[2])):
                print(f"No server backup for {cmd[2]}") # in future versions, use the closest backup to that time (or just add a submenu showing all the backups)
                continue

            print("------NOTICE------")
            c1 = input("RESTORING OLD BACKUPS OF SERVERS MAY HAVE UNINTENDED CONSEQUENCES SUCH AS LOSS OF SERVER FUNCTION. ARE YOU ABSOLUTELY SURE YOU WANT TO CONTINUE? [y/N]: ")
            if c1.lower() != "y":
                print("Aborting.")
                continue
            else:
                c2 = input(f"LAST CHANCE!! THIS WILL RESTORE THE SERVER TO ITS STATE ON {cmd[2]}!! [y/N]: ")
                if c2.lower() != "y":
                    print("Aborting.")
                    continue

            tempdirname = "SMTEMP-" + str(uuid.uuid4())

            if os.path.exists(os.path.join("..", tempdirname)):
                print(f"Error: Please delete the folder \"{tempdirname}\"")
                continue

            print("Starting rollback. (This may take a while on large servers!)")
            try:
                for thing in os.listdir(os.path.join("..", cmd[1])):
                    if thing not in ["SMBackup", "Backup"]:
                        path = os.path.join(thing)
                        
                        if os.path.isdir(path):
                            shutil.rmtree(path)
                        else:
                            os.remove(path)
                
                # Fix a bug
                try:
                    
                    os.chdir("..")
                    os.mkdir(tempdirname)
                    os.chdir(tempdirname)
                except:
                    print(f"Error: Please delete the folder \"{tempdirname}\"")
                    continue
                            
                shutil.copytree(os.path.join("..", cmd[1], "SMBackup", cmd[2]), os.path.join("..", cmd[1]), dirs_exist_ok=True)
            except Exception as e:
                print("Fatal error! Couldn't roll back server")
                print(f"Technical Details:\n{e}")
                print("Can't revert changes.")
                continue

            os.chdir("..")
            os.rmdir(tempdirname)

            print(f"Backup restored successfully!")
            
            os.chdir(originalCWD)
        else:
            print(f"Server \"{cmd[1]}\" doesn't exist. Are you sure you typed it correctly?")  
            print("Restore aborted")
            continue

        continue
        
    elif cmd.lower() == "help":
        print("reset - Factory resets ServerManager\nexit - Exit\ninfo [servers/config] - Shows information about the gives argument\n Example: info servers\nstart [serverName] - Starts the given Minecraft Server if it exists in the servers directory.\n Example: start mySMP\nbackup [serverName] - Backs up the server.\n Example: rollback mySMP\nrollback [serverName] [minutes.seconds AM/PM month.day.year]\n Example: rollback mySMP 06.05 PM 08.09.2025")
        print("\nNote: This program does NOT have the capability to CREATE servers.")
        print("This program is not a server-hosting tool.")
        print("This program is designed for Paper servers, but may work with other kinds of servers")
        continue

    elif cmd.lower() in ["undertale", "determination", "chara", "asgore", "frisk", "sans", "papyrus", "alphys", "undyne", "flowey", "asriel", "toriel", "determination", "justice"]:
        print("-----------------------")
        print("| YOU   LV %%  ###:## |")
        print("| cmd.exe             |")
        print("|   ????     Return   |")
        print("-----------------------")
        print("Can't access file.")
        print("Not enough DETERMINATION")
        

    else:
        print("Unsupported command, type \"help\" for help")
        continue