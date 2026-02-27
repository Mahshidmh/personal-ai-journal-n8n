from datetime import datetime
import json
import os
import checkfunc
from json import JSONDecodeError

#check if database exist or not.
file_path = "messages.json"
userMessage=[]

if os.path.exists(file_path):
    try:
        with open(file_path, "r") as file:
            userMessage=json.load(file)
            if not isinstance(userMessage,list):
                 userMessage=[]
    except JSONDecodeError :
         userMessage =[]

#get input from the user
while True:
    date=datetime.now().isoformat()
    text=input("what is you're message?: ").strip()
    
    if not text:
        print("you're message can't be empty")
        continue
    
    singleMessage={}

    singleMessage["text"] = text
    singleMessage["createdAt"] = date

#analysis the message that user sent.
    print(checkfunc.ifGoodOrBad(text))

#save the message in database
    userMessage.append(singleMessage)

    with open("messages.json", "w") as db:
        json.dump(userMessage,db, indent=4)

#show the whole message history       

    print(userMessage)
