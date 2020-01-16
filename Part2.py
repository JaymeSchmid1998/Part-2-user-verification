from firebase import firebase
import json
import time
import RPi.GPIO as GPIO

DoorName="TASDA"
#replace this in later versions of this code 
print("Please input your door entrance code")
doorCode=input()
print("the door code you input is..."+doorCode)

firebase = firebase.FirebaseApplication("https://pineappleverification.firebaseio.com/",None)
NumOfDoors =firebase.get('/DoorCount/node/cnt','')

#firstly i need this program to check if the user has access to the door and is authorised to access the door

DoorCount=NumOfDoors
dc=int(DoorCount)
print(dc)
checker=False
placeName=""
authlevel=""
while dc > 0 and checker == False :
    doorResult=firebase.get('/Doors/'+str(dc),'')
    doorjson=json.dumps(doorResult, sort_keys=True, indent=4)
    x=json.loads(doorjson)
    if x is not None:
        print(x)
        print(x["Status"])
        if x["DoorName"] == DoorName:
            if x["Status"]=="active":
                checker=True
                placeName=x["placeName"]
                authlevel=x["AuthLevel"]
                print("doorFound")
            else:
                print("door not active")
    dc=dc-1
    
if checker ==True:
    
    NumOfAccessRecords =firebase.get('/AccessRequestsCount/node/cnt','')
    x3=NumOfAccessRecords
    print(x3)
    x5= int(x3)
    doorAccIsFound=False
    userAuthCode=""
    while x5>0 and doorAccIsFound == False:
        doorAccResult=firebase.get('/AccessRequests/'+str(x5),'')
        doorAccjson=json.dumps(doorAccResult, sort_keys=True, indent=4)
        doorJson=json.loads(doorAccjson)
        print(doorJson["DoorCode"])
        doojint=doorJson["DoorCode"]
        dji=int(doojint)
        print (doorCode)
        if int(doorCode) == dji:
            doorAccIsFound=True
            userAuthCode=doorJson["AuthCode"]
            print("doorCode found")
            
        x5=x5-1
        
    if doorAccIsFound==True:
        NumOfUsers =firebase.get('/UserCount/node/cnt','')
        x2=NumOfUsers
        numofu=int(x2)
        userAccess=False
        while numofu >0 and userAccess==False:
            doorUserResult=firebase.get('/Users/'+str(numofu),'')
            doorUserjson=json.dumps(doorUserResult, sort_keys=True, indent=4)
            userJson=json.loads(doorUserjson)
            print(userJson["PlaceName"])
            print(userJson["AuthLevel"])
            print(userJson["AuthCode"])
            print(userJson["Status"])
            #check auth code then status then auth level and then place name
            if int(userAuthCode)==int(userJson["AuthCode"]):
                if userJson["Status"]=="active":
                    if int(userJson["AuthLevel"])==int(authlevel):
                        if userJson["PlaceName"]== placeName:
                            #this user has access to the db
                            print("access granted")
                            userAccess=True
                        
                    
                    
            numofu=numofu-1
        
    
    
    
    
    #i need to firstly check if the door access request exists and is valid
    #then i need to check if the users account has access to the door 
GPIO.setmode(GPIO.BCM)
GPIO.setup(6,GPIO.OUT)
GPIO.setup(21,GPIO.OUT)


if checker == True and doorAccIsFound ==True and userAccess==True:
    #show green led
    print("acess granted")
    GPIO.output(6,1)
    time.sleep(1)
    GPIO.output(6,0)
    
    

   
        
else:
    print("access denied")
    GPIO.output(21,1)
    time.sleep(1)
    GPIO.output(21,0)
    #show red led
GPIO.cleanup()
