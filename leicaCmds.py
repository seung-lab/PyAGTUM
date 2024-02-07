import datetime
from serial import Serial
import time

#init the serial port to the microtome
ser = Serial('COM1', 19200, timeout=2)


def calc_checksum(a):
    return hex(((sum(int(a[i:i+2],16) for i in range(0, len(a), 2))%0x100)^0xFF)+1)[2:]

def leicaMessage(Rec,Sen,Grp,Cmm,Xst,Yst):
    message_body = Rec + Sen + Grp + Cmm + Xst + Yst
    message_checksum = calc_checksum(message_body).upper()
    message_complete = '!' + message_body + message_checksum + '\r'
    return (message_complete)

def leicaTalk(Rec,Sen,Grp,Cmm,Xst,Yst,bytes2read=20):
    ser.close()
    ser.open()
#    print('Write Start = ' + datetime.datetime.now().strftime("%I:%M:%S.%f"))
    message_complete = leicaMessage(Rec, Sen, Grp, Cmm, Xst, Yst)
    # print('Command String = ' + message_complete)
    Nattempts=1;
    iattempt=0
    
    response = ''
    found=False
    if Cmm=='FF':
        for iattempt in range(Nattempts):
            try:
                ser.write(message_complete.encode())
                response = ser.read_until(b'\r',bytes2read).decode()
                if checkResponseIntegrity(response) and response.count('!')==1:
                    if response.startswith('!'+Sen+Rec+Grp+Cmm):
                        found=True
                        break;
            except:
                response = ""
                found=False;
    
        if not found:
            response='?'+ response[1:]
        
    #    print("command: {0} ({1}): {2}".format(message_complete[:-3],iattempt,response))
    else:
        try:
            ser.write(message_complete.encode())
            response = ser.read_until(b'\r',bytes2read).decode()
            if checkResponseIntegrity(response) and response.count('!')==1:
                if response.startswith('!'+Sen+Rec+Grp+Cmm):
                    found=True
        except:
            response = ""
            found=False;
    
        if not found:
            response='?'+ response[1:]
        print("wrote command: {0}, got response: {1}".format(message_complete,response))


    return response

def checkResponseIntegrity(response):
    responseChkSum = response[-3:-1]
#    print('response checksum = ' + responseChkSum)
    responseBody = response.replace('!','')[:-3]
#    print("response body = " + responseBody)
    checkCheckSum = calc_checksum(responseBody).upper().zfill(2)
#    print('checkchecksum = ' + checkCheckSum)
    if responseChkSum == checkCheckSum:
#        print('Response Checksums are equal!')
#        print()
        return 1
    else:
#        print('Checksums are NOT equal!')
#        print()
        return 0


""" N/S Stage Movement Commands -------------------------------------------------- """
# leicaTalk(Receiver,Sender,Group,Command,Xstring,Ystring)

NSctspmm = 10000  # NS counts per mm

def getNS_Abs():
    print('Get N/S Stage Position (Max 109372 mm)')
    NSresponse = leicaTalk('4','1','30','FF','','')
    time.sleep(.5)
    NSposition = float(int(NSresponse[7:-3],16)/NSctspmm)
    print('Position = ' + str(NSposition) + ' mm')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return NSposition

def stopNS_motor():
    print('Stopping N/S Motor')
    response = leicaTalk('4','1','30','00','','')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return response

def moveNS_Abs(position):
    position = int(position*NSctspmm)
    print('Move N/S Stage Position to ' + str(position) +' mm')
    posHex = hex(position)[2:].upper().zfill(6)
    response = leicaTalk('4','1','30','01',posHex,'')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return response

def initNS_motorEK1_limit():
    print('Initializing N/S Motor to EK1 Limit (South)')
    response = leicaTalk('4','1','30','02','','')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return response

def initNS_motorEK2_limit():
    print('Initializing N/S Motor to EK2 Limit (North)')
    response = leicaTalk('4','1','30','03','','')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return response

def moveNS_motorRel_South(delta):
    steps = int(delta*NSctspmm)
    stepsHex = hex(steps)[2:].upper().zfill(4)
    # print(stepsHex)
    print('Moving N/S Motor Relative, South ' + str(steps) + ' mm')
    response = leicaTalk('4','1','30','06',str(stepsHex),'')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return response

def moveNS_motorRel_North(delta):
    steps = int(delta*NSctspmm)
    stepsHex = hex(steps)[2:].upper().zfill(4)
    # print(stepsHex)
    print('Moving N/S Motor Relative, North ' + str(steps) + ' mm')
    response = leicaTalk('4','1','30','07',str(stepsHex),'')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return response

def initNS_motor_mid_limit():
    print('Initializing N/S Motor to mid-point between EK1 and EK2 Limits')
    response = leicaTalk('4','1','30','0A','01','')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return response

def NSautoSendOff():
    print('Turn off AutoSend')
    response = leicaTalk('4','1','31','01','00','')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return response

def NSautoSendOn(increment):
    print('Turn on AutoSend (increment x 250 = ms)')
    response = leicaTalk('4','1','31','01',str(increment),'')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return response

def NSautoSendStatus():
    print('NSautoSend status = ')
    response = leicaTalk('4','1','31','FF','','')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return response



""" E/W Stage Movement Commands -------------------------------------------------- """
# leicaTalk(Receiver,Sender,Group,Command,Xstring,Ystring)

EWctspmm = 10000 # counts/mm in East-West direction

def getEW_Abs():
    print('Get E/W Stage Position (Max 328,960 mm)')
    EWresponse = leicaTalk('4','1','40','FF','','')
    time.sleep(.5)
    # print('Hex Position = ' + response[7:-3])
    EWposition = 32 - float(int(EWresponse[7:-3],16)/EWctspmm) # EW encoder has zero to right so subtract from 32 to correct
    print('EWPosition = ' + str(EWposition) + ' mm')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return EWposition

def stopEW_motor():
    print('Stopping E/W Motor')
    response = leicaTalk('4','1','40','00','','')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return response

def moveEW_Abs(position):
    position = int((32-position)*EWctspmm)  # EW encoder has zero to right so subtract from 32 to correct
    print('Move E/W Stage Position to ' + str(position) +' mm')
    posHex = hex(position)[2:].upper().zfill(6)
    response = leicaTalk('4','1','40','01',posHex,'')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return response

def initEW_motorEK3_limit():
    print('Initializing E/W Motor to EK3 Limit (East)')
    response = leicaTalk('4','1','40','03','','')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return response

def initEW_motorEK4_limit():
    print('Initializing E/W Motor to EK4 Limit (West)')
    response = leicaTalk('4','1','40','02','','')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return response

def moveEW_motorRel_East(delta):
    steps = int(delta * EWctspmm)
    stepsHex = hex(steps)[2:].upper().zfill(4)
    # print(stepsHex)
    print('Moving E/W Motor Relative, East ' + str(steps) + ' mm')
    response = leicaTalk('4','1','40','07',str(stepsHex),'')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return response

def moveEW_motorRel_West(delta):
    steps = int(delta * EWctspmm)
    stepsHex = hex(steps)[2:].upper().zfill(4)
    # print(stepsHex)
    print('Moving E/W Motor Relative, West ' + str(steps) + ' mm')
    response = leicaTalk('4','1','40','06',str(stepsHex),'')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return response

def initEW_motor_mid_limit():
    print('Initializing E/W Motor to mid-point between EK3 and EK4 Limits')
    response = leicaTalk('4','1','40','0A','01','')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return response

def EWautoSendOff():
    print('Turn off AutoSend')
    response = leicaTalk('4','1','41','01','00','')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return response

def EWautoSendOn(increment):
    print('Turn on AutoSend (increment x 250 = ms)')
    response = leicaTalk('4','1','41','01',str(increment),'')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return response

def EWautoSendStatus():
    print('EWautoSend status = ')
    response = leicaTalk('4','1','41','FF','','')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return response



""" Cutting Motor / Handwheel Control Commands -------------------------------------------------- """
# leicaTalk(Receiver,Sender,Group,Command,Xstring,Ystring)

def stopCuttingMotor():
    print('Stop Cutting Motor')
    response = leicaTalk('5','1','20','00','','')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return response

def startCuttingMotor():
    print('Start Cutting Motor')
    response = leicaTalk('5','1','20','01','','')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return response

def getCuttingMotorStatus():
    print('Status Cutting Motor')
    response = leicaTalk('5','1','20','FF','','')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return response

def setFeedRate(feed):
    feedHex = hex(feed)[2:].upper().zfill(4)
    print(feedHex)
    print('Setting feed to ' + str(feed) + ' nm')
    response = leicaTalk('4','1','23','01',str(feedHex),'')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return feed

def getFeedRate():
    print('Get Feed rate')
    response = leicaTalk('4','1','23','FF','','')
    print('response: ' + response)
    time.sleep(.5)
    # print('Hex Position = ' + response[7:-3])
    feed = float(int(response[7:-3],16))
    print('Feed = ' + str(feed) + ' nm')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return feed

def setCuttingSpeed(speed):
    speedHex = hex(speed)[2:].upper().zfill(4)
    print(speedHex)
    print('Setting cutting speed to ' + str(speed/1000.0) + ' mm/s')
    response = leicaTalk('5','1','30','01',str(speedHex),'')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return speed

def getCuttingSpeed():
    print('Get Cutting Speed')
    response = leicaTalk('5','1','30','FF','','')
    time.sleep(.5)
    # print('Hex Position = ' + response[7:-3])
    speed = float(int(response[7:-3],16)/1000)
    print('Cutting Speed = ' + str(speed) + ' mm/s')
    print(datetime.datetime.now().strftime("%I:%M:%S.%f"))
    print()
    return speed

def setReturnSpeed(speed):
    speedHex = hex(speed)[2:].upper().zfill(4)
    response = leicaTalk('5','1','31','01',str(speedHex),'',20)
    return speed

def getReturnSpeed():
    response = leicaTalk('5','1','31','FF','','',20)
    if response.startswith('?'):
        speed = -1
    else:
        speed = int(response[7:11],16)
    return speed,response

def getHandwheelPosition():
    response = leicaTalk('5','1','40','FF','','')
    pos = int(response[7:11],16)
    return pos


""" Group Commands -------------------------------------------------- """
pos = [0, 0, 0]
def getAllPos():

    pos[0] = getEW_Abs()
    pos[1] = getNS_Abs()
    pos[2] = 0

    print('Pos 0 = ' + str(pos[0]))
    print('Pos 1 = ' + str(pos[1]))
    print('Pos 2 = ' + str(pos[2]))
    print()
    return pos




















































































''' UNUSED CODE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! '''

def CRAPleicaTalk(Rec,Sen,Grp,Cmm,Xst,Yst):
    message_complete = leicaMessage(Rec, Sen, Grp, Cmm, Xst, Yst)
    # print('Command String = ' + message_complete)
    ser.write(message_complete.encode())
    # response = ser.readline().decode()
    response = ser.read_until(b'\r',20).decode()
    print('System Response = ' + response)

    group = response[3:5]
    motionCmd = response[5:7]
    ser.write(leicaMessage('4', '1', group, motionCmd, '', '').encode())

    print('motionCmd = ' + motionCmd)
    motionCmd = 'YYYY'
    #if motionCmd == '01' or '06' or '07':
    if motionCmd != 'YYYY' :
        print('I AM IN THE LOOP!')
        #ser.write(leicaMessage('4', '1', '03', '01', '01', '').encode()) # turn autosend on

        limit = 10
        while limit >= 0:
            ser.write(leicaMessage('4', '1', group, motionCmd, '', '').encode())
            response = ser.read_until(b'\r', 20).decode()
            print('response1 = ' + response)
            print('response1[5:7] = ', response[5:7])
            limit -= 1
            print('Limit = ' + str(limit))

        #ser.write(leicaMessage('4', '1', '03', '00', '', '').encode()) # turn autosend off
        print()

        while response[5:7] != 'FF' :
            ser.write(leicaMessage('4', '1', group, motionCmd, '', '').encode())
            response = ser.read_until(b'\r', 20).decode()
            print('I AM IN THE WHILE!')
            print('response = ' + response)
            print('response[5:7] = ', response[5:7])
            print('response[7:9] = ', response[7:9])

            # response = ser.read_until(b'\r', 20).decode()
        else:
            print('response exiting WHILE = ', response)
    else:
        print('response exiting LOOP = ', response)
        #ser.write(leicaMessage('4', '1', '03', '00', '', '').encode())  # turn autosend off

    #integrity = checkResponseIntegrity(response)
    #return(integrity)
    return response
