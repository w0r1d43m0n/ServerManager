import os
import sys
import uuid
import shutil
from methods import *
from datetime import datetime

global configver

originalCWD = os.getcwd()
datafolder = f"{os.getenv("APPDATA")}\\servermgr\\"
expectedconfigver = 2
configver = -1

try:
    if not os.path.exists(datafolder):
        os.mkdir(datafolder)
except:
    print("fatal: ServerManager doesn't have access to your AppData directory or it does not exist.")
    print("Unrecoverable error")
    sys.exit(1)

if not os.path.exists(os.path.join(datafolder, 'servermgr.ini')):
    print("Welcome to ServerManager")
    serverPath = input("Where should ServerManager look for servers (full path)?: ")
    with open(os.path.join(datafolder, 'servermgr.ini'), 'w') as ini:
        ini.write(f"[configVer]:{expectedconfigver}\n")
        ini.write(f"[serverPath]:{serverPath}")
    os.system('cls')
    print("ServerManager v0.2-Pre_Release for Windows")
else:
    try:
        with open(os.path.join(datafolder, 'servermgr.ini'), 'r') as ini:
            lines = ini.readlines()
            configver = lines[0].replace("[configVer]:", "").replace("\n", "")
            serverPath = lines[1].replace("[serverPath]:", "").replace("\n", "")
            for i in [configver, serverPath]: # check if any values are empty
                if i == "":
                    raise IndexError() # skip to except clause
    except IndexError as e:
        print("fatal: ServerManager's config wasn't initialized correctly. Resetting ServerManager.")
        os.remove(os.path.join(datafolder, 'servermgr.ini'))
        print("ServerManager reset")
        sys.exit(1)

    print("ServerManager v0.2-Pre_Release for Windows")

try:
    servers = next(os.walk(serverPath))[1] # https://stackoverflow.com/questions/973473/getting-a-list-of-all-subdirectories-in-the-current-directory/973488#973488
except:
    print("fatal: server path does not exist!")
    os.remove(os.path.join(datafolder, 'servermgr.ini'))
    print("ServerManager reset. Quitting.")
    sys.exit(1)

print("Type \"help\" for a list of commands")
while True:
    try:
        cmd = input("> ")
    except KeyboardInterrupt:
        print("exit")
        print("Quitting.")
        sys.exit(0)

    if cmd.lower() == "reset":
        os.remove(os.path.join(datafolder, 'servermgr.ini'))
        print("ServerManager reset")
        sys.exit(0)

    elif cmd.lower() == "exit":
        print("Quitting.")
        sys.exit(0)

    elif cmd.lower() in ["clear", "cls"]:
        os.system("cls")
        print("ServerManager v0.2-Pre_Release for Windows")
        print("Type \"help\" for a list of commands")
        continue

    elif cmd.lower().startswith("info "):
        cmd = cmd.split(' ')
        if len(cmd) != 2:
            print("Malformed command, type \"help\" for help")
            continue
        if cmd[1] == "servers":
            for server in servers:
                if os.path.exists(os.path.join(serverPath, server, "start.bat")): # Is a compatible server
                    print(f"Server: \"{server}\"")
                    sys.stdout.write("Server size: Calculating...\r")
                    sys.stdout.flush()
                    print(f"Server size: {getFolderSize(serverPath, file_exclusions=[], folder_exclusions=["SMBackup", "Backup"], to="auto")}              ")
                    sys.stdout.write("Backup size: Calculating...\r")
                    sys.stdout.flush()
                    print(f"Backup size: {getFolderSize(os.path.join(serverPath, server, "SMBackup"), to="auto")}              ")
                    print(f"Creation date: guessed {datetime.fromtimestamp(os.path.getctime(os.path.join(serverPath, server, "start.bat"))).strftime("%I:%M %p %m/%d/%Y")}")
                    print(f"Server version: {getMCServerVersion(os.path.join(serverPath, server))}")
                    print(f"Server type: {getMCServerHoster(os.path.join(serverPath, server))}")
                else:
                    print(f"\"{server}\" is not a Minecraft server, skipping...")
        elif cmd[1] == "config":
            if os.path.exists(os.path.join(datafolder, 'servermgr.ini')):
                print(f"servermgr.ini file is located at {os.path.join(datafolder, 'servermgr.ini')}")
                print(f"servermgr.ini file manifest version: {configver}")
                print(f"Searching for servers at \"{serverPath}\"")
        else:
            print("Malformed command, type \"help\" for help")
    
    elif cmd.lower().startswith("start "):
        cmd = cmd.split(' ')
        if len(cmd) != 2:
            print("Malformed command, type \"help\" for help")
            continue
        if cmd[1] in servers:
            print(f"Starting server \"{cmd[1]}\".")
            os.chdir(os.path.join(serverPath, cmd[1]))
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
            os.chdir(os.path.join(serverPath, cmd[1]))
            if not os.path.exists("SMBackup"):
                print("Folder \"SMBackup\" does not exist. Creating it.")
                os.mkdir("SMBackup")

            backupFolder = os.path.join("SMBackup", datetime.now().strftime("%I.%M %p %m.%d.%Y"))

            print("Starting backup. (This may take a while on large servers!)")
            try:
                shutil.copytree(".", backupFolder, ignore=shutil.ignore_patterns("Backup", "SMBackup"))
            except Exception as e:
                print("fatal: couldn't back up server")
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

            os.chdir(os.path.join(serverPath, cmd[1]))
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
                print("fatal: couldn't roll back server")
                print(f"Technical Details:\n{e}")
                print("Can't revert changes.")
                continue

            os.chdir("..")
            os.rmdir(tempdirname)

            print(f"Backup restored successfully!")
            
            os.chdir(originalCWD)
        else:
            print(f"Server \"{cmd[1]}\" doesn't exist. Are you sure you typed it correctly?")
            continue

        continue
        
    elif cmd.lower() == "help":
        print("reset - Factory resets ServerManager\nexit - Exit\ninfo [servers/config] - Shows information about the gives argument\n Example: info servers\nstart [serverName] - Starts the given Minecraft Server if it exists in the servers directory.\n Example: start mySMP\nbackup [serverName] - Backs up the server.\n Example: backup mySMP\nrollback [serverName] [minutes.seconds AM/PM month.day.year]\n Example: rollback mySMP 06.05 PM 08.09.2025")
        print("\nNote: This program does NOT have the capability to CREATE servers.")
        print("This program is not a server-hosting tool.")
        print("This program is designed for Paper servers, but may work with other kinds of servers")
        continue

    elif cmd.lower() == "test":
        getMCServerHoster(os.path.join(serverPath, "SMP"))

    elif cmd == "SaveFile0": # obligatory undertale reference
        print("-----------------------")
        print("| YOU   LV %%  ###:## |")
        print("| cmd.exe             |")
        print("|   ????     Return   |")
        print("-----------------------")
        print("PermissionError: You are not in the .reseters file!")

    else:
        print("Unsupported command, type \"help\" for help")
        continue