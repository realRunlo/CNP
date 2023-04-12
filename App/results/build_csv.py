import csv, os , re

FILENAME = "measurements.csv"

# List with the values of the csv's header
header_list = ["Zone", "Time", "Bandwidth", 
               "Jitter (To Server)", 
               "Jitter (From Server)",
               "Packet Loss (To Server)",
               "Packet Loss (From Server)",
               "Bit Rate (With UDP - To Server)", 
               "Bit Rate (With UDP - From Server)", 
               "Bit Rate (With TCP - To Server)",
               "Bit Rate (With TCP - From Server)"]

"""
TODO:
- Arranjar forma de saber o nome da zona do servidor (buscar o nome da diretoria onde estão os ficheiros de teste???)
- Arranjar forma de conseguir o timestamp dos testes (deve chegar Ano, Mes, Dia, Hora, Minuto)
- Corrigir para adicionar só uma vez o header
- Automatizar o processo de adicionar novas entradas no csv à medida que vamos fazendo os testes
"""

def append_line(line_list):
    """ Append a new line in the file "measurements.csv" """
    with open(FILENAME, 'a+', newline='') as f_object:
	    writer_object = csv.writer(f_object)
	    writer_object.writerow(line_list)
	    f_object.close()
    return f_object


def get_zones (filepath):
    """Get all the zones in a list"""
    ls = [name for name in os.listdir(filepath) if os.path.isdir(name)] 
    for l in ls:
        re.sub('./', '', l)
    return ls


def process_files (zone, bdw_file, udp_file, tcp_file):
    """Handles all the three files from tests and append a line in the csv file"""
    r = []

    bitrate_udp_fromServer = bitrate_udp_toServer = bitrate_tcp_fromServer = bitrate_tcp_toServer = jitter_fromServer = jitter_toServer = packetloss_fromServer = packetloss_toServer = bandwidth = ""

    bandwidth = get_bandwidth(bdw_file)
    bitrate_udp_fromServer, bitrate_udp_toServer, jitter_fromServer, jitter_toServer, packetloss_fromServer, packetloss_toServer = get_bitrate_jitter_packet_loss_UDP(udp_file)
    bitrate_tcp_fromServer, bitrate_tcp_toServer = get_bitrate_jitter_packet_loss_TCP(tcp_file)

    r.append(zone)
    r.append("TIMESTAMP A DEFINIR")
    r.append(bandwidth)
    r.append(jitter_fromServer)
    r.append(jitter_toServer)
    r.append(packetloss_fromServer)
    r.append(packetloss_toServer)
    r.append(bitrate_udp_fromServer)
    r.append(bitrate_udp_toServer)
    r.append(bitrate_tcp_fromServer)
    r.append(bitrate_tcp_toServer)

    return r

def get_bandwidth(filename):
    """Gets the bandwidth from file (the returned value type is String)"""
    reg_exp = r'\[  \d+\] \d+.\d+-\d+.\d+ sec   \d+ KBytes  (?P<bandwidth>\-?(\d+\.?\d*|\d*\.?\d+)) Kbits\/sec'
    columns_pattern = re.compile(reg_exp)
    bandwidth = ""
    bdw_file_fp = open(filename, "r")
    lines_udp_file_fp = bdw_file_fp.read().splitlines()
    for line in lines_udp_file_fp:
        matches = columns_pattern.finditer(line)
        for match in matches:
            bandwidth = match.group("bandwidth")
    bdw_file_fp.close()
    return bandwidth

def get_bitrate_jitter_packet_loss_UDP(filename):
    """Gets the bitrate (from and to server), jitter (from and to server), packet loss (from and to server) from the UDP test"""
    # Digital number regex: "\-?(\d+\.?\d*|\d*\.?\d+)"
    reg_exp = r'\[  \d+\]   \d+.\d+-\d+.\d+  sec  \d+.\d+ MBytes  (?P<bitrate>\-?(\d+\.?\d*|\d*\.?\d+)) Mbits\/sec  (?P<jitter>\-?(\d+\.?\d*|\d*\.?\d+)) ms  \d+\/\d+ \((?P<packetloss>\-?(\d+\.?\d*|\d*\.?\d+))%\)  (?P<origin>\w+)'
    columns_pattern = re.compile(reg_exp)

    udp_file_fp = open(filename, "r")

    bitrate_fromServer = bitrate_toServer = bitrate = jitter = jitter_fromServer = jitter_toServer = packetloss_fromServer = packetloss_toServer = packetloss = origin = ""
    
    lines_udp_file_fp = udp_file_fp.read().splitlines()
    for line in lines_udp_file_fp:
        matches = columns_pattern.finditer(line)
        for match in matches:
            bitrate = match.group("bitrate")
            jitter = match.group("jitter")
            packetloss = match.group("packetloss")
            origin = match.group("origin")
            #print((bitrate, jitter, packetloss, origin))
            if (bitrate != "" and jitter != "" and packetloss != "" and origin != ""):
                if (origin == "sender"):
                    bitrate_toServer = bitrate
                    jitter_toServer = jitter
                    packetloss_toServer = packetloss
                elif (origin == "receiver"):
                    bitrate_fromServer = bitrate
                    jitter_fromServer = jitter
                    packetloss_fromServer = packetloss
                print("UDP: " + str((bitrate_fromServer, bitrate_toServer, jitter_fromServer, jitter_toServer, packetloss_fromServer, packetloss_toServer)))

    udp_file_fp.close()
    return (bitrate_fromServer, bitrate_toServer, jitter_fromServer, jitter_toServer, packetloss_fromServer, packetloss_toServer)


def get_bitrate_jitter_packet_loss_TCP(filename):
    """Gets the bitrate (from and to server) from TCP file"""

    reg_exp = r'\[  \d+\]   \d+.\d+-\d+.\d+  sec  \d+.\d+ MBytes  (?P<bitrate>\-?(\d+\.?\d*|\d*\.?\d+)) Mbits/sec                  (?P<origin>\w+)'
    columns_pattern = re.compile(reg_exp)
    
    bitrate = bitrate_fromServer = bitrate_toServer = origin = ""

    tcp_file_fp = open(filename, "r")

    lines_tcp_file_fp = tcp_file_fp.read().splitlines()
    for line in lines_tcp_file_fp:
        matches = columns_pattern.finditer(line)
        for match in matches:
            bitrate = match.group("bitrate")
            origin = match.group("origin")
            # print((bitrate, origin))
            if (bitrate != "" and origin != ""):
                if (origin == "sender"):
                    bitrate_toServer = bitrate
                elif (origin == "receiver"):
                    bitrate_fromServer = bitrate
                print("TCP: " + str((bitrate_toServer, bitrate_fromServer)))


    tcp_file_fp.close()
    return (bitrate_toServer, bitrate_fromServer)


    
# Create the header in csv file
append_line(header_list) 
line_to_add = process_files("ZONA A DEFINIR", 
                            "europe-west1-b/bandwidth.txt", 
                            "europe-west1-b/udp.txt",
                            "europe-west1-b/tcp.txt")

append_line(line_to_add)