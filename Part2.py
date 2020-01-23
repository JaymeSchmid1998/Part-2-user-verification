import RPi.GPIO as GPIO
import Keypad
from firebase import firebase
import json
import time


from pathlib import *
# coding: utf-8


ROWS = 4
COLS = 4
keys = 	[	'1','2','3','A',
		'4','5','6','B',
	    	'7','8','9','C',
    		'*','0','#','D'		]
rowsPins = [12,16,18,22]
colsPins = [19,15,13,11]

DoorName="TASDA"

def loop():  
    keypad = Keypad.Keypad(keys,rowsPins,colsPins,ROWS,COLS)
    keypad.setDebounceTime(50)
    test = 1
    storedvalue=''                          
    while(test == 1):
        key = keypad.getKey()
        if(key != keypad.NULL):
            print ("You Pressed Key : %c "%(key) )
            if key=='#':
                    #
                print("test")
                checker(storedvalue)
                test=0
            elif key=='C':
                storedvalue = storedvalue[:-1]
                print(storedvalue)                                              
            else:
                storedvalue =storedvalue + key
                print(storedvalue)
                                            
                                            
def checker(doorCode):
    from firebase import firebase
    #start
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
    GPIO.cleanup()           
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(6,GPIO.OUT)
    GPIO.setup(12,GPIO.OUT)
    if checker == True and doorAccIsFound ==True and userAccess==True:
    #show green led
        print("acess granted")
        GPIO.output(6,1)
        time.sleep(1)
        GPIO.output(6,0)
        openDoor()
    else:
        print("access denied")
        GPIO.output(12,1)
        time.sleep(1)
        GPIO.output(12,0)
    #show red led
    GPIO.cleanup()
    #end
def openDoor():
    GPIO.setmode(GPIO.BCM)

    ControlPin=[26,19,13,5]

    for pin in ControlPin:
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin,0)
    
    seq= [ [1,0,0,0],
          [1,1,0,0],
          [0,1,0,0],
          [0,1,1,0],
          [0,0,1,0],
          [0,0,1,1],
          [0,0,0,1],
          [1,0,0,1]]

    for i in range(128):
        for halfstep in range(8):
            for pin in range(4):
                #print(ControlPin[pin])
                #print(seq[halfstep][pin])
                GPIO.output(ControlPin[pin],seq[halfstep][pin])
            
            time.sleep(0.00001)
        
    GPIO.cleanup()
    
    
    
    
    
if __name__ == '__main__':     # Program start from here
	
	try:
            retry=1
            while retry==1:
                print("Please input your door entrance code")
                loop()
	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
	    	GPIO.cleanup()
