import sys
import socket
from threading import Thread
from datetime import datetime

PROBE_PACKETS = 3
PORT = 6666


def server_handler(message,address,utc_now,UDPServerSocket):
    message_decoded = message.decode('utf-8').split(";")
    print(message_decoded[1])
   
    # transform string timestamp to datetime object
    client_stamp = datetime.strptime(message_decoded[1],"%Y-%m-%d %H:%M:%S.%f")
   
    t_delta = utc_now - client_stamp
    
    delta_ms = t_delta.total_seconds() * 1000
    response_massage = str(message_decoded[0]) + ";" + str(delta_ms)
    response = str.encode(response_massage)
    # Sending a reply to client
    UDPServerSocket.sendto(response, address)

if __name__ == "__main__":
    

    if sys.argv[1]=="-s":

        probe_counter = 0
        bufferSize  = 1024

        # Create a datagram socket
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        # Bind to address and ip
        UDPServerSocket.bind(('', PORT))
        print("UDP server up and listening")
        
        # Listen for incoming datagrams
        while(True):
            if probe_counter == PROBE_PACKETS:
                sys.exit()
            bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

            probe_counter +=1 
                
            message = bytesAddressPair[0]

            address = bytesAddressPair[1]

            # get the current time in the local timezone
            utc_now = datetime.utcnow() 

            thread = Thread(target=server_handler,args=(message,address,utc_now,UDPServerSocket))
            thread.start()
    elif sys.argv[1]=="-c":
  
        packet_id = 0

        serverAddressPort   = (sys.argv[2], PORT)

        bufferSize          = 1024

        # Create a UDP socket at client side
        UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        for i in range(PROBE_PACKETS):

            # get the current time in utc
            utc_now = datetime.utcnow()

            packet = str(packet_id) + ";" + str(utc_now)

            bytesToSend         = str.encode(packet)

            UDPClientSocket.sendto(bytesToSend, serverAddressPort)

            packet_id += 1
        
        response_counter = 0 
        # Send to server using created UDP socket
        while(True):
            if response_counter == PROBE_PACKETS:
                sys.exit()
            msgFromServer = UDPClientSocket.recvfrom(bufferSize)
            response_counter +=1
            message = msgFromServer[0]
            message_decoded = message.decode('utf-8').split(";")

            print(message_decoded[1])

 