import csv, os , re, sys, datetime, statistics

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

def process_files (zone, bdw_file,udp_file, tcp_file, owd_file):
    """Handles all the four files from tests and append a line in the csv file"""
    r = []

    max_bitrate_udp = max_bitrate_tcp = bitrate_udp_download = bitrate_udp_upload = bitrate_tcp_download = bitrate_tcp_upload = jitter_download = jitter_upload = packetloss_download = packetloss_upload = bandwidth = owd = ""

    timestamp = get_timestamp()
    bandwidth = get_bandwidth(bdw_file)
    max_bitrate_tcp = get_max_bitrate_tcp(tcp_file)
    bitrate_udp_download, bitrate_udp_upload, jitter_download, jitter_upload, packetloss_download, packetloss_upload = get_bitrate_jitter_packet_loss_UDP(udp_file)
    bitrate_tcp_download, bitrate_tcp_upload = get_bitrate_jitter_packet_loss_TCP(tcp_file)
    owd = get_one_way_delay(owd_file)

    r.append(zone)
    r.append(timestamp)
    r.append(bandwidth)
    r.append(jitter_download)
    r.append(jitter_upload)
    r.append(packetloss_download)
    r.append(packetloss_upload)
    r.append(bitrate_tcp_download)
    r.append(bitrate_tcp_upload)
    r.append(max_bitrate_tcp)
    r.append(owd)

    return r

def get_bandwidth(filename):
    """Gets the bandwidth from file (the returned value type is String)"""
    reg_exp = r'\[\s+\d+\]\s+\-?(\d+\.?\d*|\d*\.?\d+)\-\-?(\d+\.?\d*|\d*\.?\d+)\s+\w+\s+\-?(\d+\.?\d*|\d*\.?\d+)\s+\w+\s+(?P<bandwidth>\-?(\d+\.?\d*|\d*\.?\d+)\s+\w)\w+\/\w+'
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
    reg_exp = r'\[\s+\d+\]\s+\d+.\d+-\d+.\d+\s+sec\s+\d+.\d+\s+MBytes\s+(?P<bitrate>\-?(\d+\.?\d*|\d*\.?\d+)\s+\w)bits\/sec\s+(?P<jitter>\-?(\d+\.?\d*|\d*\.?\d+))\s+ms\s+\d+\/\d+\s+\((?P<packetloss>\-?(\d+\.?\d*|\d*\.?\d+))%\)\s+(?P<origin>\w+)'
    columns_pattern = re.compile(reg_exp)

    udp_file_fp = open(filename, "r")

    bitrate_download = bitrate_upload = bitrate = jitter = jitter_download = jitter_upload = packetloss_download = packetloss_upload = packetloss = origin = ""
    
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
                    bitrate_upload = bitrate
                    jitter_upload = jitter
                    packetloss_upload = packetloss
                elif (origin == "receiver"):
                    bitrate_download = bitrate
                    jitter_download = jitter
                    packetloss_download = packetloss
                #print("UDP: " + str((bitrate_download, bitrate_upload, jitter_download, jitter_upload, packetloss_download, packetloss_upload)))

    udp_file_fp.close()
    return (bitrate_download, bitrate_upload, jitter_download, jitter_upload, packetloss_download, packetloss_upload)


def get_bitrate_jitter_packet_loss_TCP(filename):
    """Gets the bitrate (from and to server) from TCP file"""

    reg_exp = r'\[\s+\d+\]\s+\d+.\d+-\d+.\d+\s+sec\s+\d+.\d+\s+MBytes\s+(?P<bitrate>\-?(\d+\.?\d*|\d*\.?\d+)\s+\w)bits\/sec\s+(?P<origin>\w+)'
    columns_pattern = re.compile(reg_exp)
    
    bitrate = bitrate_download = bitrate_upload = origin = ""

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
                    bitrate_upload = bitrate
                elif (origin == "receiver"):
                    bitrate_download = bitrate
                #print("TCP: " + str((bitrate_upload, bitrate_download)))


    tcp_file_fp.close()
    return (bitrate_upload, bitrate_download)

def get_max_bitrate_tcp(filename):
    """Get maximum bitrate from tcp file"""
    reg_exp = r'^\[\s+\d+\]\s+\d+.\d+-\d+.\d+\s+sec\s+\d+.\d+\s+MBytes\s+(?P<bitrate>\-?(\d+\.?\d*|\d*\.?\d+)\s+\w)bits\/sec\s+$'
    columns_pattern = re.compile(reg_exp)

    bitrate = ""
    all_bitrates_stored = []

    tcp_file_fp = open(filename, "r")

    lines_tcp_file_fp = tcp_file_fp.read().splitlines()
    for line in lines_tcp_file_fp:
        matches = columns_pattern.finditer(line)
        for match in matches:
            bitrate = match.group("bitrate")
            medida = bitrate[-2:]
            bitrate = bitrate[:-2]
            all_bitrates_stored.append(float(bitrate))

    tcp_file_fp.close()
    #print("TCP" + str(all_bitrates_stored))

    return str(max(all_bitrates_stored)) + medida

def get_max_bitrate_udp(filename):
    """Get maximum bitrate from udp file"""
    reg_exp = r'^\[\s*\d+\]\s+\d+\.\d+-\d+\.\d+\s+sec\s+\d+\s+KBytes\s+(?P<bitrate>\-?(\d+\.?\d*|\d*\.?\d+)\s+\w)bits\/sec\s+\d+\s+$'
    columns_pattern = re.compile(reg_exp)

    bitrate = ""
    all_bitrates_stored = []

    tcp_file_fp = open(filename, "r")

    lines_tcp_file_fp = tcp_file_fp.read().splitlines()
    for line in lines_tcp_file_fp:
        matches = columns_pattern.finditer(line)
        for match in matches:
            bitrate = match.group("bitrate")
            medida = bitrate[-2:]
            bitrate = bitrate[:-2]
            all_bitrates_stored.append(float(bitrate))

    tcp_file_fp.close()
    #print("UDP" + str(all_bitrates_stored))
    return str(max(all_bitrates_stored)) + medida


def get_one_way_delay(filename):
    """Get maximum one way delay from owd file"""
    reg_exp = r'(?P<owd>\-?(\d+\.?\d*|\d*\.?\d+))'
    columns_pattern = re.compile(reg_exp)

    owd = ""
    all_owd_stored = []

    owd_file_fp = open(filename, "r")

    lines_owd_file_fp = owd_file_fp.read().splitlines()
    for line in lines_owd_file_fp:
        matches = columns_pattern.finditer(line)
        for match in matches:
            owd = match.group("owd")
            all_owd_stored.append(float(owd))

    owd_file_fp.close()
    #print("UDP" + str(all_bitrates_stored))

    return str('%.2f' % statistics.mean(all_owd_stored))


if __name__ == "__main__":
    # Get the zone given as argument    
    zone = sys.argv[1]

    FILENAME = "measurements.csv"

    # List with the values of the csv's header
    header_list = ["Zone", 
                   "Datetime", 
                   "Bandwidth", 
                   "Upload Jitter", 
                   "Download Jitter",
                   "Upload Packet Loss",
                   "Download Packet Loss", 
                   "Upload Bit Rate (With TCP)",
                   "Download Bit Rate (With TCP)",
                   "Max Bit Rate (With TCP)",
                   "One-Way Delay"
                ]

    line_to_add = process_files(zone,
                                "results/temp/bandwidth.txt",
                                "results/temp/udp.txt",
                                "results/temp/tcp.txt",
                                "results/temp/owd.txt")

    if not os.path.isfile(FILENAME) or os.stat(FILENAME).st_size == 0:
        with open(FILENAME, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header_list)
            writer.writerow(line_to_add)
    else:
        with open(FILENAME, 'a+', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(line_to_add)
