# -*- coding: utf-8 -*-

import serial
import time

conn = serial.Serial('COM6') # ttyACM1 for Arduino board
conn.timeout=2
readOut = 0   #chars waiting from laser range finder

print ("Syringe pump connected")


def find_pumps(conn,tot_range=10):
    pumps = []
    for i in range(tot_range):
        cmd='*ADR %i\x0D'%i
        conn.write(cmd.encode())
        output = conn.readline()
        if len(output)>0:
            pumps.append(i)
    return pumps

def run_all(conn):
    cmd = '*RUN\x0D'
    conn.write(cmd.encode())
    output = conn.readline()
    if '?' in output.decode("utf-8"): print(cmd.strip()+' from run_all not understood')

def stop_all(conn):
    cmd = '*STP\x0D'
    conn.write(cmd.encode())
    output = conn.readline()
    if '?' in output.decode("utf-8"): print(cmd.strip()+' from stop_all not understood')

def stop_pump(conn,pump):
    cmd = '%iSTP\x0D'%pump
    conn.write(cmd.encode())
    output = conn.readline()
    if '?' in output.decode("utf-8"): print(cmd.strip()+' from stop_pump not understood')

    cmd = '%iRAT0UH\x0D'%pump
    conn.write(cmd.encode())
    output = conn.readline()
    if '?' in output.decode("utf-8"): print(cmd.strip()+' from stop_pump not understood')

def set_rates(conn,rates,pumps):
    cmd = ''
    for pump in pumps:
        flowrate = float(rates[pump])
        direction = 'INF'
        if flowrate<0: direction = 'WDR'
        frcmd = '%iDIR %s\x0D'%(pump,direction)
        conn.write(frcmd.encode())
        output = conn.readline()
        if '?' in output.decode("utf-8"): print(cmd.strip()+' from set_rate not understood')
        fr = abs(flowrate)
                
        if fr<5000:
            cmd += str(pump)+'RAT'+str(fr)[:5]+'UH*'
        else:
            fr = fr/1000.0
            cmd += str(pump)+'RAT'+str(fr)[:5]+'MH*'
    cmd += '\x0D'
    conn.write(cmd.encode())
    output = conn.readline()
    if '?' in output.decode("utf-8"): print(cmd.strip()+' from set_rates not understood')

def get_rate(conn,pump):
    #get direction
    cmd = '%iDIR\x0D'%pump
    conn.write(cmd.encode())
    output = conn.readline()
    sign = ''
    if output[4:7]=='WDR':
        sign = '-'
    cmd = '%iRAT\x0D'%pump
    conn.write(cmd.encode())
    output = conn.readline()
    if '?' in output.decode("utf-8"): print(cmd.strip()+' from get_rate not understood')

    print("output: ",output)
    units = output[-3:-1]
    print('units: {0}'.format(units))
    if units=='MH':
        rate = str(float(output[4:-3])*1000)
    if units=='UH':
        rate = output[4:-3]
    return sign+rate

def get_rates(conn,pumps):
    rates = dict((p,get_rate(conn,p).split('.')[0]) for p in pumps)
    return rates

def set_diameter(conn,pump,dia):
    cmd = '%iDIA %s\x0D'%(pump,dia)
    conn.write(cmd.encode())
    output = conn.readline()
    if '?' in output.decode("utf-8"): print(cmd.strip()+' from set_diameter not understood')

    
def get_diameter(conn,pump):
    cmd = '%iDIA\x0D'%pump
    conn.write(cmd.encode())
    output = conn.readline()
    if '?' in output.decode("utf-8"): print(cmd.strip()+' from get_diameter not understood')
    dia = output[4:-1]
    return dia

def prime(conn,pump):
    # set infuse direction
    cmd = '%iDIR INF\x0D'%pump
    conn.write(cmd.encode())
    output = conn.readline()
    if '?' in output.decode("utf-8"): print(cmd.strip()+' from prime not understood')

    # set rate
    cmd = '%iRAT10.0MH\x0D'%pump
    conn.write(cmd.encode())
    output = conn.readline()
    if '?' in output.decode("utf-8"): print(cmd.strip()+' from prime not understood')

    # run
    cmd = '%iRUN\x0D'%pump
    conn.write(cmd.encode())
    output = conn.readline()
    if '?' in output.decode("utf-8"): print(cmd.strip()+' from prime not understood')





#ser = serial.Serial('COM3',19200)
#print conn.name       # check which port was really used
#print conn.isOpen()
#conn.close()
#pumps = find_pumps(conn)
#rates = get_rates(conn,pumps)
