import xyzStageCmds
import leicaCmds as Leica
import atumCmds_2 as Atum
from tkinter import *
import threading
import time

import logging

Stages = xyzStageCmds.stages(3) # need to specify the number of axes to create


def setPickupPosition():
    Stages.setPickupPositionNoOffset()
    return



def createLabels():

    # Stages labels
    lblStagesName = Label(window, text="STAGES", font=("Arial Bold", 20), bg='dark sea green', relief="sunken", borderwidth=5)
    lblStagesName.place(x=25, y=20, width=200, height=110)

    lblStagesPos = Label(window, text="Position", font=("Arial", 20))
    lblStagesPos.place(x=50, y=165, width=150, height=50)

    lblStagesPickup = Label(window, text="Pickup", font=("Arial", 20))
    lblStagesPickup.place(x=50, y=250, width=150, height=50)

    lblStagesMoveTo = Label(window, text="Move To", font=("Arial", 20))
    lblStagesMoveTo.place(x=50, y=350, width=150, height=60)

    lblStagesJog = Label(window, text="Jog", font=("Arial", 20))
    lblStagesJog.place(x=50, y=430, width=150, height=60)

    lblStagesX = Label(window, text="X", font=("Arial Bold", 30))
    lblStagesX.place(x=250, y=0, width=150, height=85)
    lblStagesX = Label(window, text="(mm)\n[0-300]", font=("Arial", 14))
    lblStagesX.place(x=250, y=75, width=150, height=65)

    lblStagesY = Label(window, text="Y", font=("Arial Bold", 30))
    lblStagesY.place(x=450, y=0, width=150, height=85)
    lblStagesY = Label(window, text="(mm)\n[0-75]", font=("Arial", 14))
    lblStagesY.place(x=450, y=75, width=150, height=65)

    lblStagesZ = Label(window, text="Z", font=("Arial Bold", 30))
    lblStagesZ.place(x=650, y=0, width=150, height=85)
    lblStagesZ = Label(window, text="(mm)\n[0-75]", font=("Arial", 14))
    lblStagesZ.place(x=650, y=75, width=150, height=65)

    # ATUM labels
    lblDivide1 = Label(window, bg='dark sea green') # DRAWS GREEN DIVIDER BAR BETWEEN DEVICES
    lblDivide1.place(x=875, y=0, width=5, height=850)

    lblP = Label(window, text="ATUM", font=("Arial Bold", 20), bg='dark sea green', relief="sunken", borderwidth=5)
    lblP.place(x=925, y=20, width=200, height=110)

    lblAtumSet = Label(window, text="Current", font=("Arial", 20))
    lblAtumSet.place(x=950, y=165, width=150, height=60)
    lblAtumSet = Label(window, text="Set", font=("Arial", 20))
    lblAtumSet.place(x=950, y=250, width=150, height=60)

    lblTapeSpeed = Label(window, text="Speed", font=("Arial Bold", 24))
    lblTapeSpeed.place(x=1150, y=0, width=150, height=85)
    lblTapeSpeed = Label(window, text="(mm/s)\n[0-10]", font=("Arial", 14))
    lblTapeSpeed.place(x=1150, y=75, width=150, height=65)

    lblTapeTension = Label(window, text="Tension", font=("Arial Bold", 24))
    lblTapeTension.place(x=1325, y=0, width=200, height=85)
    lblTapeTension = Label(window, text="(%)\n[0-100]", font=("Arial", 14))
    lblTapeTension.place(x=1350, y=75, width=150, height=65)

    # Leica labels
    lblDivide2 = Label(window, bg='dark sea green') # DRAWS GREEN DIVIDER BAR BETWEEN DEVICES
    lblDivide2.place(x=1600, y=0, width=5, height=850)

    lblLeicaName = Label(window, text="LEICA", font=("Arial Bold", 20), bg='dark sea green', relief="sunken", borderwidth=5)
    lblLeicaName.place(x=1650, y=20, width=200, height=110)

    lblLeicaPos = Label(window, text="Position", font=("Arial", 20))
    lblLeicaPos.place(x=1675, y=165, width=150, height=50)

    lblLeicaPickup = Label(window, text="Pickup", font=("Arial", 20))
    lblLeicaPickup.place(x=1675, y=250, width=150, height=50)

    lblLeicaMoveTo = Label(window, text="Move To", font=("Arial", 20))
    lblLeicaMoveTo.place(x=1675, y=350, width=150, height=60)

    lblLeicaJog = Label(window, text="Jog", font=("Arial", 20))
    lblLeicaJog.place(x=1675, y=430, width=150, height=60)

    lblLeicaX = Label(window, text="E-W", font=("Arial Bold", 30))
    lblLeicaX.place(x=1875, y=0, width=150, height=85)
    lblLeicaX = Label(window, text="(mm)\n[0-32]", font=("Arial", 14))
    lblLeicaX.place(x=1875, y=75, width=150, height=65)

    lblLeicaY = Label(window, text="N-S", font=("Arial Bold", 30))
    lblLeicaY.place(x=2075, y=0, width=150, height=85)
    lblLeicaY = Label(window, text="(mm)\n[0-10]", font=("Arial", 14))
    lblLeicaY.place(x=2075, y=75, width=150, height=65)

    lblLeicaZ = Label(window, text="R", font=("Arial Bold", 30))
    lblLeicaZ.place(x=2275, y=0, width=150, height=85)
    lblLeicaZ = Label(window, text="(NA)\n[NA]", font=("Arial", 14))
    lblLeicaZ.place(x=2275, y=75, width=150, height=65)


def updateReadouts():
    lblStagesXval.config(text='{:6.3f}'.format(Stages.getAllPos()[0]))
    lblStagesYval.config(text='{:6.3f}'.format(Stages.getAllPos()[1]))
    lblStagesZval.config(text='{:6.3f}'.format(Stages.getAllPos()[2]))

    lblStagesPickupXval.config(text='{:6.3f}'.format(Stages.pickupPosition[0]))
    lblStagesPickupYval.config(text='{:6.3f}'.format(Stages.pickupPosition[1]))
    lblStagesPickupZval.config(text='{:6.3f}'.format(Stages.pickupPosition[2]))

    lblTapeSpeedval.config(text='{:6.2f}'.format(Atum.gTS()))
    lblTapeTensionval.config(text='{:3.0f}'.format(Atum.gTT()))

    window.after(250, updateReadouts)


def updateLeicaReadouts():
    #time.sleep(.5)
    pos = Leica.getAllPos()
    lblLeicaEWval.config(text='{:6.3f}'.format(float(pos[0])))  #Leica.getEW_Abs()))
    lblLeicaNSval.config(text='{:6.3f}'.format(float(pos[1])))   #Leica.getNS_Abs()))
    lblLeicaRval.config(text='{:6.3f}'.format(0))

    # window.after(250, updateReadouts)


def setupButtons():

    # Stages buttons
    btnStagesMoveToX = Button(window, text='►', command=clkStagesMoveToX, font=("Arial Bold", 15), bg='azure3')
    btnStagesMoveToX.place(x=250, y=350, width=30, height=60)
    btnStagesMoveToY = Button(window, text='►', command=clkStagesMoveToY, font=("Arial Bold", 15), bg='azure3')
    btnStagesMoveToY.place(x=450, y=350, width=30, height=60)
    btnStagesMoveToZ = Button(window, text='►', command=clkStagesMoveToZ, font=("Arial Bold", 15), bg='azure3')
    btnStagesMoveToZ.place(x=650, y=350, width=30, height=60)

    btnStagesJogXplus = Button(window, text='▲', command=clkStagesJogXplus, font=("Arial Bold", 15), bg='azure3')
    btnStagesJogXplus.place(x=250, y=430, width=30, height=30)
    btnStagesJogXminus = Button(window, text='▼', command=clkStagesJogXminus, font=("Arial", 15), bg='azure3')
    btnStagesJogXminus.place(x=250, y=460, width=30, height=30)
    btnStagesJogYplus = Button(window, text='▲', command=clkStagesJogYplus, font=("Arial", 15), bg='azure3')
    btnStagesJogYplus.place(x=450, y=430, width=30, height=30)
    btnStagesJogYminus = Button(window, text='▼', command=clkStagesJogYminus, font=("Arial", 15), bg='azure3')
    btnStagesJogYminus.place(x=450, y=460, width=30, height=30)
    btnStagesJogZplus = Button(window, text='▲', command=clkStagesJogZplus, font=("Arial", 15), bg='azure3')
    btnStagesJogZplus.place(x=650, y=430, width=30, height=30)
    btnStagesJogZminus = Button(window, text='▼', command=clkStagesJogZminus, font=("Arial", 15), bg='azure3')
    btnStagesJogZminus.place(x=650, y=460, width=30, height=30)

    btnStagesHomeAll = Button(window, text="Home\nAll", command=clkStagesHome, font=("Arial", 18), bg='azure3')
    btnStagesHomeAll.place(x=50, y=550, width=150, height=100)

    btnStagesStow = Button(window, text="Stow\nAll", command=clkStagesStow, font=("Arial", 18), bg='azure3')
    btnStagesStow.place(x=250, y=550, width=150, height=100)

    btnStagesSetPickup = Button(window, text="Set As\nPickup", command=clkStagesSetPickup, font=("Arial", 18), bg='azure3')
    btnStagesSetPickup.place(x=450, y=550, width=150, height=100)

    btnStagesMoveToPickup = Button(window, text='Move To\nPickup', command=clkStagesMoveToPickup, font=("Arial", 18), bg='azure3')
    btnStagesMoveToPickup.place(x=650, y=550, width=150, height=100)


    # ATUM buttons
    btnSetSpeed = Button(window, text='►', command=clkAtumSetSpeed, font=("Arial Bold", 20), bg='azure3')
    btnSetSpeed.place(x=1150, y=250, width=30, height=60)

    btnSetTension = Button(window, text='►', command=clkAtumSetTension, font=("Arial Bold", 20), bg='azure3')
    btnSetTension.place(x=1350, y=250, width=30, height=60)

    btnAtumStart = Button(window, text='Start', command=clkAtumStart, font=("Arial", 18), bg='azure3')
    btnAtumStart.place(x=950, y=370, width=150, height=100)

    btnAtumStop = Button(window, text='Stop', command=clkAtumStop, font=("Arial", 18), bg='azure3')
    btnAtumStop.place(x=1150, y=370, width=150, height=100)

    btnAtumReverse = Button(window, text='Reverse', command=clkAtumReverse, font=("Arial", 18), bg='azure3')
    btnAtumReverse.place(x=1350, y=370, width=150, height=100)


    # Leica buttons
    btnLeicaMoveToX = Button(window, text='►', command=clkLeicaMoveToX, font=("Arial Bold", 15), bg='azure3')
    btnLeicaMoveToX.place(x=1875, y=350, width=30, height=60)
    btnLeicaMoveToY = Button(window, text='►', command=clkLeicaMoveToY, font=("Arial Bold", 15), bg='azure3')
    btnLeicaMoveToY.place(x=2075, y=350, width=30, height=60)
    btnLeicaMoveToZ = Button(window, text='►', command=clkLeicaMoveToZ, font=("Arial Bold", 15), bg='azure3')
    btnLeicaMoveToZ.place(x=2275, y=350, width=30, height=60)

    btnLeicaJogXplus = Button(window, text='▲', command=clkLeicaJogXplus, font=("Arial Bold", 15), bg='azure3')
    btnLeicaJogXplus.place(x=1875, y=430, width=30, height=30)
    btnLeicaJogXminus = Button(window, text='▼', command=clkLeicaJogXminus, font=("Arial", 15), bg='azure3')
    btnLeicaJogXminus.place(x=1875, y=460, width=30, height=30)
    btnLeicaJogYplus = Button(window, text='▲', command=clkLeicaJogYplus, font=("Arial", 15), bg='azure3')
    btnLeicaJogYplus.place(x=2075, y=430, width=30, height=30)
    btnLeicaJogYminus = Button(window, text='▼', command=clkLeicaJogYminus, font=("Arial", 15), bg='azure3')
    btnLeicaJogYminus.place(x=2075, y=460, width=30, height=30)
    btnLeicaJogZplus = Button(window, text='▲', command=clkLeicaJogZplus, font=("Arial", 15), bg='azure3')
    btnLeicaJogZplus.place(x=2275, y=430, width=30, height=30)
    btnLeicaJogZminus = Button(window, text='▼', command=clkLeicaJogZminus, font=("Arial", 15), bg='azure3')
    btnLeicaJogZminus.place(x=2275, y=460, width=30, height=30)

    btnLeicaHomeAll = Button(window, text="Home\nAll", command=clkLeicaHome, font=("Arial", 18), bg='azure3')
    btnLeicaHomeAll.place(x=1675, y=550, width=150, height=100)

    btnLeicaStow = Button(window, text="Stow\nAll", command=clkLeicaStow, font=("Arial", 18), bg='azure3')
    btnLeicaStow.place(x=1875, y=550, width=150, height=100)

    btnLeicaSetPickup = Button(window, text="Set As\nPickup", command=clkLeicaSetPickup, font=("Arial", 18), bg='azure3')
    btnLeicaSetPickup.place(x=2075, y=550, width=150, height=100)

    btnLeicaStart = Button(window, text="Start", command=clkLeicaStart, font=("Arial", 18), bg='azure3')
    btnLeicaStart.place(x=1675, y=700, width=150, height=100)

    btnLeicaStop = Button(window, text="Stop", command=clkLeicaStop, font=("Arial", 18), bg='azure3')
    btnLeicaStop.place(x=1875, y=700, width=150, height=100)

    #btnLeicaMoveToPickup = Button(window, text='Move To\nPickup', command=clkLeicaMoveToPickup, font=("Arial", 18), bg='azure3')
    #btnLeicaMoveToPickup.place(x=2275, y=570, width=150, height=100)

def setupStagesParkingButton():
    parkingAction = Stages.getParkState()[0]
    parkingColor = Stages.getParkState()[1]
    btnStagesParking = Button(window, text=parkingAction, command=clkStagesParking, font=("Arial Bold", 24), bg=parkingColor) #'azure3')
    btnStagesParking.place(x=50, y=700, width=350, height=100)

def setupLeicaParkingButton():
    parkingAction = '1' # s.getParkState()[0]
    parkingColor = '1' # s.getParkState()[1]
    btnLeicaParking = Button(window, text=parkingAction, command=clkLeicaParking, font=("Arial Bold", 24), bg=parkingColor) #'azure3')
    btnLeicaParking.place(x=50, y=700, width=350, height=100)


'''   SET UP STAGES CLICK EVENTS   '''

def clkStagesHome():
    Stages.homeAll()

def clkStagesStow():
    Stages.moveToStow()

def clkStagesSetPickup():
    Stages.setPickupPositionNoOffset()

def clkStagesMoveToPickup():
    Stages.moveToPickup()
    clkStagesParking()

def clkStagesParking():
    action = Stages.getParkState()[0]
    print('Action = ' + action)
    if action == "Unpark":
        Stages.Unpark()
        setupStagesParkingButton()
    else:
        Stages.Park()
        setupStagesParkingButton()


# move-to button clicks
def clkStagesMoveToX():
    move = abs(float(lblStagesMoveToX.get()))
    lblStagesMoveToX.delete(0,END)
    lblStagesMoveToX.insert(0,str(move))
    Stages.moveXabs(move)

def clkStagesMoveToY():
    move = abs(float(lblStagesMoveToY.get()))
    lblStagesMoveToY.delete(0,END)
    lblStagesMoveToY.insert(0,str(move))
    Stages.moveYabs(move)

def clkStagesMoveToZ():
    move = abs(float(lblStagesMoveToZ.get()))
    lblStagesMoveToZ.delete(0,END)
    lblStagesMoveToZ.insert(0,str(move))
    Stages.moveZabs(move)


# jog button clicks
def clkStagesJogXplus():
    jog = abs(float(lblStagesJogX.get()))
    lblStagesJogX.delete(0,END)
    lblStagesJogX.insert(0,str(jog))
    Stages.moveXrel(jog)

def clkStagesJogXminus():
    jog = abs(float(lblStagesJogX.get()))
    lblStagesJogX.delete(0,END)
    lblStagesJogX.insert(0,str(jog))
    Stages.moveXrel(-jog)

def clkStagesJogYplus():
    jog = abs(float(lblStagesJogY.get()))
    lblStagesJogY.delete(0,END)
    lblStagesJogY.insert(0,str(jog))
    Stages.moveYrel(jog)

def clkStagesJogYminus():
    jog = abs(float(lblStagesJogY.get()))
    lblStagesJogY.delete(0,END)
    lblStagesJogY.insert(0,str(jog))
    Stages.moveYrel(-jog)

def clkStagesJogZplus():
    jog = abs(float(lblStagesJogZ.get()))
    lblStagesJogZ.delete(0,END)
    lblStagesJogZ.insert(0,str(jog))
    Stages.moveZrel(jog)

def clkStagesJogZminus():
    jog = abs(float(lblStagesJogZ.get()))
    lblStagesJogZ.delete(0,END)
    lblStagesJogZ.insert(0,str(jog))
    Stages.moveZrel(-jog)


'''   SET UP ATUM CLICK EVENTS   '''

def initializeAtumettings():
    speed = str(Atum.gTS())
    lblAtumSetSpeed.delete(0, END)
    lblAtumSetSpeed.insert(0, str(speed))

    tension = str(int(Atum.gTT()))
    lblAtumSetTension.delete(0, END)
    lblAtumSetTension.insert(0, tension)

def clkAtumSetSpeed(speed=None):
    if speed==None:
        speed = Atum.gTS()
        print('Old Speed = ' + str(speed))
        speed = float(lblAtumSetSpeed.get())
    if speed > 10:
        speed = 10
    if speed < 0:
        speed = 0
    print('New Speed = ' + str(speed))
    lblAtumSetSpeed.delete(0, END)
    lblAtumSetSpeed.insert(0, str(speed))
    Atum.sTS(speed)

def clkAtumSetTension():
    tension = int(float(lblAtumSetTension.get()))
    if tension > 100:
        tension = 100
    if tension < 0:
        tension = 0
    print('Tension = ' + str(tension))
    lblAtumSetTension.delete(0, END)
    lblAtumSetTension.insert(0, str(tension))
    Atum.sTT(int(tension))

def clkAtumStart():
    Atum.Start()


def clkAtumStop():
    Atum.Stop()


def clkAtumReverse():
    Atum.Reverse()


'''   SET UP LEICA CLICK EVENTS   '''

def clkLeicaHome():
    Leica.initNS_motor_mid_limit()
    Leica.initEW_motor_mid_limit()
    updateLeicaReadouts()
    updateLeicaReadouts()
    return

def clkLeicaStow():
    # s.moveToStow()
    updateLeicaReadouts()
    updateLeicaReadouts()
    return

def clkLeicaSetPickup():
    # s.setPickupPositionNoOffset()
    updateLeicaReadouts()
    updateLeicaReadouts()
    return

def clkLeicaMoveToPickup():
    # s.moveToPickup()
    clkLeicaParking()

def clkLeicaParking():
    # action = s.getParkState()[0]
    # print('Action = ' + action)
    # if action == "Unpark":
        # s.Unpark()
        # setupLeicaParkingButton()
    # else:
        # s.Park()
        # setupLeicaParkingButton()
    updateLeicaReadouts()
    updateLeicaReadouts()
    return

# move-to button clicks
def clkLeicaMoveToX():
    move = abs(float(lblLeicaMoveToX.get()))
    lblLeicaMoveToX.delete(0,END)
    lblLeicaMoveToX.insert(0,str(move))
    Leica.moveEW_Abs(move)
    updateLeicaReadouts()
    updateLeicaReadouts()

def clkLeicaMoveToY():
    move = abs(float(lblLeicaMoveToY.get()))
    lblLeicaMoveToY.delete(0,END)
    lblLeicaMoveToY.insert(0,str(move))
    Leica.moveNS_Abs(move)
    updateLeicaReadouts()
    updateLeicaReadouts()

def clkLeicaMoveToZ():
    move = abs(float(lblLeicaMoveToZ.get()))
    lblLeicaMoveToZ.delete(0,END)
    lblLeicaMoveToZ.insert(0,str(move))
    # s.moveZabs(move)
    updateLeicaReadouts()
    updateLeicaReadouts()




# jog button clicks
def clkLeicaJogXplus():
    jog = abs(float(lblLeicaJogX.get()))
    lblLeicaJogX.delete(0,END)
    lblLeicaJogX.insert(0,str(jog))
    Leica.moveEW_motorRel_West(jog)
    updateLeicaReadouts()
    updateLeicaReadouts()

def clkLeicaJogXminus():
    jog = abs(float(lblLeicaJogX.get()))
    lblLeicaJogX.delete(0,END)
    lblLeicaJogX.insert(0,str(jog))
    Leica.moveEW_motorRel_East(jog)
    updateLeicaReadouts()
    updateLeicaReadouts()

def clkLeicaJogYplus():
    jog = abs(float(lblLeicaJogY.get()))
    lblLeicaJogY.delete(0,END)
    lblLeicaJogY.insert(0,str(jog))
    Leica.moveNS_motorRel_North(jog)
    updateLeicaReadouts()
    updateLeicaReadouts()

def clkLeicaJogYminus():
    jog = abs(float(lblLeicaJogY.get()))
    lblLeicaJogY.delete(0,END)
    lblLeicaJogY.insert(0,str(jog))
    Leica.moveNS_motorRel_South(jog)
    updateLeicaReadouts()
    updateLeicaReadouts()

def clkLeicaJogZplus():
    jog = abs(float(lblLeicaJogZ.get()))
    lblLeicaJogZ.delete(0,END)
    lblLeicaJogZ.insert(0,str(jog))
    # s.moveZrel(jog)
    updateLeicaReadouts()
    updateLeicaReadouts()

def clkLeicaJogZminus():
    jog = abs(float(lblLeicaJogZ.get()))
    lblLeicaJogZ.delete(0,END)
    lblLeicaJogZ.insert(0,str(jog))
    # s.moveZrel(-jog)
    updateLeicaReadouts()
    updateLeicaReadouts()

def clkLeicaStart():
    Leica.startCuttingMotor()
    updateLeicaReadouts()

def clkLeicaStop():
    Leica.stopCuttingMotor()
    updateLeicaReadouts()



'''   GENERATE UI WINDOW   '''

window = Tk()

window.title("PNI ATUM Hardware Console")
window.geometry('2450x850')


'''   SET UP READOUTS'''
# Stages
lblStagesXval = Label(window, text='{:6.3f}'.format(Stages.getAllPos()[0]), font=("Arial", 20), bg='white')
lblStagesXval.place(x=250, y=165, width=150, height=50)
lblStagesYval = Label(window, text='{:6.3f}'.format(Stages.getAllPos()[1]), font=("Arial", 20), bg='white')
lblStagesYval.place(x=450, y=165, width=150, height=50)
lblStagesZval = Label(window, text='{:6.3f}'.format(Stages.getAllPos()[2]), font=("Arial", 20), bg='white')
lblStagesZval.place(x=650, y=165, width=150, height=50)

lblStagesPickupXval = Label(window, text='{:6.3f}'.format(Stages.pickupPosition[0]), font=("Arial", 20)) #, bg='white')
lblStagesPickupXval.place(x=250, y=250, width=150, height=50)
lblStagesPickupYval = Label(window, text='{:6.3f}'.format(Stages.pickupPosition[1]), font=("Arial", 20)) #, bg='white')
lblStagesPickupYval.place(x=450, y=250, width=150, height=50)
lblStagesPickupZval = Label(window, text='{:6.3f}'.format(Stages.pickupPosition[2]), font=("Arial", 20)) #, bg='white')
lblStagesPickupZval.place(x=650, y=250, width=150, height=50)

# ATUM
lblTapeSpeedval = Label(window, text='{:6.2f}'.format(Atum.gTS()), font=("Arial", 20), bg='white', justify=CENTER)
lblTapeSpeedval.place(x=1150, y=165, width=150, height=50)
lblTapeTensionval = Label(window, text='{:3.0f}'.format(Atum.gTT()), font=("Arial", 20), bg='white', justify=CENTER)
lblTapeTensionval.place(x=1350, y=165, width=150, height=50)

# Leica
pos = Leica.getAllPos()
lblLeicaEWval = Label(window, text='{:6.3f}'.format(float(pos[0])), font=("Arial", 20), bg='white')
lblLeicaEWval.place(x=1875, y=165, width=150, height=50)
lblLeicaNSval = Label(window, text='{:6.3f}'.format(float(pos[1])), font=("Arial", 20), bg='white')
lblLeicaNSval.place(x=2075, y=165, width=150, height=50)
lblLeicaRval = Label(window, text='{:6.3f}'.format(0), font=("Arial", 20), bg='white')
lblLeicaRval.place(x=2275, y=165, width=150, height=50)


'''  SETUP ENTRY WINDOWS   '''
# Stages
lblStagesMoveToX = Entry(window, font=("Arial", 20), bg='mint cream', justify=CENTER )
lblStagesMoveToX.place(x=280, y=350, width=120, height=60)
lblStagesMoveToY = Entry(window, font=("Arial", 20), bg='mint cream', justify=CENTER )
lblStagesMoveToY.place(x=480, y=350, width=120, height=60)
lblStagesMoveToZ = Entry(window, font=("Arial", 20), bg='mint cream', justify=CENTER )
lblStagesMoveToZ.place(x=680, y=350, width=120, height=60)

lblStagesJogX = Entry(window, font=("Arial", 20), bg='mint cream', justify=CENTER )
lblStagesJogX.place(x=280, y=430, width=120, height=60)
lblStagesJogY = Entry(window, font=("Arial", 20), bg='mint cream', justify=CENTER )
lblStagesJogY.place(x=480, y=430, width=120, height=60)
lblStagesJogZ = Entry(window, font=("Arial", 20), bg='mint cream', justify=CENTER )
lblStagesJogZ.place(x=680, y=430, width=120, height=60)

# ATUM
lblAtumSetSpeed = Entry(window, font=("Arial", 20), bg='mint cream', justify=CENTER )
lblAtumSetSpeed.place(x=1180, y=250, width=120, height=60)

lblAtumSetTension = Entry(window, font=("Arial", 20), bg='mint cream', justify=CENTER )
lblAtumSetTension.place(x=1380, y=250, width=120, height=60)

# Leica
lblLeicaMoveToX = Entry(window, font=("Arial", 20), bg='mint cream', justify=CENTER )
lblLeicaMoveToX.place(x=1905, y=350, width=120, height=60)
lblLeicaMoveToY = Entry(window, font=("Arial", 20), bg='mint cream', justify=CENTER )
lblLeicaMoveToY.place(x=2105, y=350, width=120, height=60)
lblLeicaMoveToZ = Entry(window, font=("Arial", 20), bg='mint cream', justify=CENTER )
lblLeicaMoveToZ.place(x=2305, y=350, width=120, height=60)


lblLeicaJogX = Entry(window, font=("Arial", 20), bg='mint cream', justify=CENTER )
lblLeicaJogX.place(x=1905, y=430, width=120, height=60)
lblLeicaJogY = Entry(window, font=("Arial", 20), bg='mint cream', justify=CENTER )
lblLeicaJogY.place(x=2105, y=430, width=120, height=60)
lblLeicaJogZ = Entry(window, font=("Arial", 20), bg='mint cream', justify=CENTER )
lblLeicaJogZ.place(x=2305, y=430, width=120, height=60)



'''   CREATE ALL WIDGETS   '''
createLabels()
setupButtons()
setupStagesParkingButton()
# setupLeicaParkingButton()
updateReadouts()
initializeAtumettings()
window.mainloop()


