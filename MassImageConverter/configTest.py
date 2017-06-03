import os
import configparser

config = configparser.ConfigParser()

config.read("config.ini")

print(config.get("UserInfo", "lastOpenDir"))

config.set("UserInfo", "lastOpenDir", ";lkj;lkj")

with open("config.ini", "w") as configFile:
    config.write(configFile)

#config.set("UserInfo", "lastOpenDir", r";kljlkjh")

#with open(r"config.ini", "wb") as configFile:
#    config.write(configFile)