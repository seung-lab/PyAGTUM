from zaber.serial import AsciiSerial, AsciiDevice, AsciiCommand, AsciiReply, AsciiAxis


import time



class stages:

    ctspmm = 10078  # counts per mm
    zPosOffset = 0.5
    stowPosition = [0, 0, 75]
    pickupPosition = stowPosition

    def __init__(self, axis):

        self.port = AsciiSerial("COM4")   #com port identified using Zaber console, which was used to renumber axes too
        self.device = [None] * axis
        self.drive = [None] * axis

        for n in range(axis):
            i = n + 1
            print(i)
            self.device[n] = 'device{0}'.format(i)
            self.drive[n] = 'drive{0}'.format(i)
            print(self.device[n])
            print(self.drive[n])
            self.device[n] = AsciiDevice(self.port, i) #.poll_until_idle(i)
            self.drive[n] = self.device[n].axis(1)

    def Disconnect(self):
        self.port.close()
        return

    def Connect(self):
        self.port.open()
        return

    def homeAll(self):
        self.moveZabs(75)
        self.moveYabs(0)
        self.moveXabs(0)
        self.drive[0].home()
        self.drive[1].home()
        self.drive[2].home()
        self.moveYabs(0)

    # Relative moves
    def moveAllRel(self,*argv):
        if len(argv) != len(self.drive):
            print("invalid number of arguments")
        else:
            self.moveZrel(argv[2])
            self.moveYrel(argv[1])
            self.moveXrel(argv[0])

    def moveXrel(self, move):
        pos = int(self.drive[0].send('get pos').data) / self.ctspmm
        if (move > 0 and pos + move > 300) or (move < 0 and pos + move < 0):
            print('Xpos = ' + str(pos) + ', Move = ' + str(move))
            print("Move out of range of 0 to 300")
        else:
            self.drive[0].move_rel(int(move * self.ctspmm))

    def moveYrel(self, move):
        pos = 75 - int(self.drive[1].send('get pos').data) / self.ctspmm
        if (move > 0 and pos + move > 75) or (move < 0 and pos + move < 0):
            print('Ypos = ' + str(pos) + ', Move = ' + str(move))
            print("Move out of range of 0 to 75")
        else:
            self.drive[1].move_rel(int( -move * self.ctspmm))

    def moveZrel(self, move):
        pos = 75 - int(self.drive[2].send('get pos').data) / self.ctspmm
        if (move > 0 and pos + move > 75) or (move < 0 and pos + move < 0):
            print('Zpos = ' + str(pos) + ', Move = ' + str(move))
            print("Move out of range of 0 to 75")
        else:
            self.drive[2].move_rel(int( -move * self.ctspmm))

    #Absolute moves
    def moveAllAbs(self,*argv):
        if len(argv) != len(self.drive):
            print("invalid number of arguments")
        else:
            self.moveZabs(argv[2])
            self.moveYabs(argv[1])
            self.moveXabs(argv[0])

    def moveXabs(self, move):
        if move > 300 or move < 0:
            print("Move out of range of 0 to 300")
        else:
            self.drive[0].move_abs(int(move * self.ctspmm))

    def moveYabs(self, move):
        if move > 75 or move < 0:
            print("Move out of range of 0 to 75")
        else:
            self.drive[1].move_abs(int((75 - move) * self.ctspmm))

    def moveZabs(self, move):
        if move > 75 or move < 0:
            print("Move out of range of 0 to 75")
        else:
            self.drive[2].move_abs(int((75 - move) * self.ctspmm))


    def getAllPos(self):
        pos = [0, 0, 0]
        pos[0] = int(self.drive[0].send('get pos').data) / self.ctspmm
        pos[1] = 75 - int(self.drive[1].send('get pos').data) / self.ctspmm
        pos[2] = 75 - int(self.drive[2].send('get pos').data) / self.ctspmm

        return pos

    def moveToStow(self):
        self.moveZabs(75)  # position after homing
        self.moveYabs(0)  # position after homing
        self.moveXabs(0)  # positon after homing

        return

    def setPickupPositionNoOffset(self):
        self.pickupPosition = self.getAllPos()

        return self.pickupPosition

    def setPickupPositionWithOffset(self):
        self.pickupPosition = self.getAllPos()
        self.pickupPosition[2] += self.zPosOffset # move up in Z by offset to clear boat bottom

        return self.pickupPosition

    def moveToPickup(self):
        self.moveZabs(75) # move Z to top of stroke to avoid collisions
        self.moveYabs(0) # move Y to zero to avoid collisions

        self.moveXabs(self.pickupPosition[0]) # move to X pickup position
        self.moveYabs(self.pickupPosition[1]) # move to Y pickup position
        self.moveZabs(self.pickupPosition[2]) # finally drop down to Z pickup position

    def EStop(self):
        self.device[0].send("1 estop")
        self.device[1].send("2 estop")
        self.device[2].send("3 estop")
        return

    def Park(self):
        self.device[0].send("tools parking park")
        self.device[1].send("tools parking park")
        self.device[2].send("tools parking park")
        return

    def Unpark(self):
        self.device[0].send("tools parking unpark")
        self.device[1].send("tools parking unpark")
        self.device[2].send("tools parking unpark")
        return

    def getParkState(self):
        if str(self.device[0].send("tools parking state"))[-3:-2] == '1' or str(self.device[1].send("tools parking state"))[-3:-2] == '1' or str(self.device[2].send("tools parking state"))[-3:-2] == '1':
            action = "Unpark"
            color = "orange red"
        else:
            action = "Park"
            color = "pale green"
        return [action , color]




