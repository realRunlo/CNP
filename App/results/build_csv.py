import csv, os , re, sys, datetime

FILENAME = "measurements.csv"

# List with the values of the csv's header
header_list = ["Zone", 
               "Datetime", 
               "Bandwidth", 
               "Upload Jitter", 
               "Download Jitter",
               "Upload Packet Loss",
               "Download Packet Loss",
               "Upload Bit Rate (With UDP)", 
               "Download Bit Rate (With UDP)", 
               "Upload Bit Rate (With TCP)",
               "Download Bit Rate (With TCP)"
               ]


"""
TODO:
- [Ver se função ansible funciona] Automatizar o processo de adicionar novas entradas no csv à medida que vamos fazendo os testes
"""

def append_line(line_list):
    """ Append a new line in the file "measurements.csv" """
    with open(FILENAME, 'a+', newline='') as f_object:
	    writer_object = csv.writer(f_object)
	    writer_object.writerow(line_list)
	    f_object.close()
    return f_object


def get_timestamp ():
    """Get timestamp "Month/Day Hour/Minute" and day of the week (in string)"""
    now = datetime.datetime.now()

    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute
    day_of_week = get_day_of_week(2023, month, day)
    month = get_month(month)

    #Example: Monday 13 April 18:13
    return str(day_of_week) + " " + str(day) + " " + str(month) + " " + str(hour) + ":" + str(minute)

def get_day_of_week(ano,mes,dia):
    """Get the day of the week"""
    intDay = datetime.date(year=ano, month=mes, day=dia).weekday()
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[intDay]

def get_month(mes):
    """Get the month of the year"""
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    return months[mes-1]

def process_files (zone, bdw_file, udp_file, tcp_file):
    """Handles all the three files from tests and append a line in the csv file"""
    r = []

    bitrate_udp_fromServer = bitrate_udp_toServer = bitrate_tcp_fromServer = bitrate_tcp_toServer = jitter_fromServer = jitter_toServer = packetloss_fromServer = packetloss_toServer = bandwidth = ""

    timestamp = get_timestamp()
    bandwidth = get_bandwidth(bdw_file)
    bitrate_udp_fromServer, bitrate_udp_toServer, jitter_fromServer, jitter_toServer, packetloss_fromServer, packetloss_toServer = get_bitrate_jitter_packet_loss_UDP(udp_file)
    bitrate_tcp_fromServer, bitrate_tcp_toServer = get_bitrate_jitter_packet_loss_TCP(tcp_file)

    r.append(zone)
    r.append(timestamp)
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
                #print("UDP: " + str((bitrate_fromServer, bitrate_toServer, jitter_fromServer, jitter_toServer, packetloss_fromServer, packetloss_toServer)))

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
                #print("TCP: " + str((bitrate_toServer, bitrate_fromServer)))


    tcp_file_fp.close()
    return (bitrate_toServer, bitrate_fromServer)


# Get the zone given as argument    
zone = sys.argv[1]

line_to_add = process_files(zone,
                            zone + "/bandwidth.txt", 
                            zone + "/udp.txt",
                            zone + "/tcp.txt")

if not os.path.isfile(FILENAME) or os.stat(FILENAME).st_size == 0:
    with open(FILENAME, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header_list)
        writer.writerow(line_to_add)
else:
    with open(FILENAME, 'a+', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(line_to_add)
