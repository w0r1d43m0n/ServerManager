import os

def getMCServerHoster(serverPath):
    version = getMCServerVersion(serverPath, onlyVersionNumber=True)
    if version != -1:
        serverjar = os.listdir(os.path.join(serverPath, "versions", version))
        if len(serverjar) > 1:
            return "multiple server files found" # Change this to only use .jar files in future
        elif len(serverjar) == 1:
            serverjar = serverjar[0]
            if "paper" in serverjar.lower(): # There's gotta be a better way to do this
                return "Paper"
            elif "pufferfish" in serverjar.lower():
                return "Pufferfish"
            elif "purpur" in serverjar.lower():
                return "Purpur"
            elif "spigot" in serverjar.lower():
                return "Spigot"
            elif "fabric" in serverjar.lower():
                return "Fabric"
            elif "forge" in serverjar.lower():
                return "Forge"
            elif "sponge" in serverjar.lower():
                return "Sponge"
            elif "airplane" in serverjar.lower():
                return "Airplane"
            elif "tuinity" in serverjar.lower():
                return "Tuinity"
            else:
                return "Vanilla/Other"
        elif len(serverjar) < 1:
            return "No versions detected"
    else:
        return "Couldn't guess server runtime"

def getMCServerVersion(serverPath, onlyVersionNumber=False):
    version = os.listdir(os.path.join(serverPath, "versions"))
    if not onlyVersionNumber:
        if len(version) > 1:
            return "multiple versions or broken installation"
        elif len(version) == 1:
            return "guessed " + version[0]
        elif len(version) < 1:
            return "no versions detected"
    else:
        if len(version) != 1:
            return -1
        else:
            return version[0]

def getFolderSize(folder, file_exclusions=[], folder_exclusions=[], to="bytes"): # Adapted from https://stackoverflow.com/questions/1392413/calculating-a-directorys-size-using-python/#4368431
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath) and item not in file_exclusions:
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath) and item not in folder_exclusions:
            total_size += getFolderSize(itempath, file_exclusions=file_exclusions, folder_exclusions=folder_exclusions)

    units = {"bytes": 1, "kilobytes": 1024, "megabytes": 1024**2, "gigabytes": 1024**3}

    if to == "auto":
        if total_size >= units["gigabytes"]:
            return str(round(total_size / units["gigabytes"], 2)) + "GB"
        elif total_size >= units["megabytes"]:
            return str(round(total_size / units["megabytes"], 2)) + "MB"
        elif total_size >= units["kilobytes"]:
            return str(round(total_size / units["kilobytes"], 2)) + "KB"
        else:
            return total_size, "B"
    else:
        factor = units.get(to.lower(), 1)
        return round(total_size / factor, 2)