import serial
import time

conn = serial.Serial('COM6') # ttyACM1 for Arduino board
conn.timeout=2
readOut = 0   #chars waiting from laser range finder

print ("Starting up")
connected = False


commandToSend = '1DIR\x0D'
print("Writing: ", commandToSend)
conn.write(commandToSend.encode())
time.sleep(1)

print("Attempt to Read")
readOut = conn.readline().decode("utf-8")
time.sleep(1)
print("Reading: ", readOut[4:-1])
return


commandToSend = '1DIA20.05\x0D'
print("Writing: ", commandToSend)
conn.write(commandToSend.encode())
time.sleep(1)

commandToSend = '1DIA\x0D'
print("Writing: ", commandToSend)
conn.write(commandToSend.encode())
time.sleep(1)

print("Attempt to Read")
readOut = conn.readline().decode('ascii')
#readOut = conn.readline().decode('utf-8')
time.sleep(1)
print("Reading: ", readOut)


commandToSend = '1PHN 1\x0D'
print("Writing: ", commandToSend)
conn.write(commandToSend.encode())
time.sleep(1)

commandToSend = '1PHN\x0D'
print("Writing: ", commandToSend)
conn.write(commandToSend.encode())
time.sleep(1)

print("Attempt to Read")
readOut = conn.readline().decode('ascii')
# readOut = conn.readline().decode('utf-8')
time.sleep(1)
print("Reading: ", readOut)


commandToSend = '1VOL 05.00\x0D'
print("Writing: ", commandToSend)
conn.write(commandToSend.encode())
time.sleep(1)

commandToSend = '1VOL UL\x0D'
print("Writing: ", commandToSend)
conn.write(commandToSend.encode())
time.sleep(1)

commandToSend = '1VOL\x0D'
print("Writing: ", commandToSend)
conn.write(commandToSend.encode())
time.sleep(1)

print("Attempt to Read")
readOut = conn.readline().decode('ascii')
# readOut = conn.readline().decode('utf-8')
time.sleep(1)
print("Reading: ", readOut)


commandToSend = '1DIR INF\x0D'
print("Writing: ", commandToSend)
conn.write(commandToSend.encode())
time.sleep(1)

commandToSend = '1DIR\x0D'
print("Writing: ", commandToSend)
conn.write(commandToSend.encode())
time.sleep(1)

print("Attempt to Read")
readOut = conn.readline().decode('ascii')
# readOut = conn.readline().decode('utf-8')
time.sleep(1)
print("Reading: ", readOut[4:-1])

for i in range(0,10):
    commandToSend = '1RUN 1\x0D'
    print("Writing: ", commandToSend)
    conn.write(commandToSend.encode())
    time.sleep(1)
    print("Attempt to Read")
    readOut = conn.readline().decode('ascii')
    # readOut = conn.readline().decode('utf-8')
    print("Reading: ", readOut)
    time.sleep(1)

commandToSend = '1DIR WDR\x0D'
print("Writing: ", commandToSend)
conn.write(commandToSend.encode())
time.sleep(1)

commandToSend = '1DIR\x0D'
print("Writing: ", commandToSend)
conn.write(commandToSend.encode())
time.sleep(1)

print("Attempt to Read")
readOut = conn.readline().decode('ascii')
# readOut = conn.readline().decode('utf-8')
time.sleep(1)
 dia = readOut[4:-1]
print("Reading: ", dia)

while True:
    print ("Writing: ",  commandToSend)
    conn.write(commandToSend.encode())
    time.sleep(1)
    while True:
        try:
            print ("Attempt to Read")
            readOut = conn.readline().decode('ascii')
            #readOut = conn.readline().decode('utf-8')
            time.sleep(1)
            print ("Reading: ", readOut)
            break
        except:
            pass
    print ("Restart")
    conn.flush() #flush the buffer