#!/usr/bin/python
from lxml import etree
import os
import sys
import manuf

def run(mac_parser):
    print "[*] NETXML to CSV Converter"

    if len(sys.argv) != 3:
        print "[*] Usage: %s input output" % sys.argv[0]
    else:
        input_file_name = sys.argv[1]
        output_base_filename = sys.argv[2]
        output_AP_filename = output_base_filename + '_ap.csv'
        output_clients_filename = output_base_filename + '_clients.csv'
        if input_file_name != output_base_filename:
            try:
                output_AP_handler = file(output_AP_filename, 'w')
            except:
                print "[-] Unable to create output file '%s' for writing." % output_AP_filename
                exit()
            try:
                output_clients_handler = file(output_clients_filename, 'w')
            except:
                print "[-] Unable to create output file '%s' for writing." % output_clients_filename
                exit()

            try:
                doc = etree.parse(input_file_name)
            except:
                print "[-] Unable to open input file: '%s'." % input_file_name
                exit()

            print "[+] Parsing '%s'." % input_file_name
            # parsing netxml for access points
            sys.stdout.write("[+] Outputting Access Points to '%s' " % output_AP_filename)
            output_AP_handler.write("BSSID,MACVendor,Channel,Privacy,Cypher,Auth,PowerMin,PowerMax,ESSID,Clients,DateMin,DateMax,Datasize,Lat,Lon\n")
            result, clients = parse_net_xml(doc,mac_parser)
            output_AP_handler.write(result)
            sys.stdout.write(" Complete.\r\n")

            # using gathered results for clients
            sys.stdout.write("[+] Outputting Clients to '%s' " % output_clients_filename)
            output_clients_handler.write("ClientMAC,MACVendor,PowerMax,BSSID,ESSID\n")
            for client_list in clients:
                for client in client_list:
                    output_clients_handler.write('"%s","%s","%s","%s","%s"\n' % (client[0], client[1], client[2], client[3], client[4]))
            sys.stdout.write(" Complete.\r\n")

def parse_net_xml(doc,mac_parser):
    result = ""

    total = len(list(doc.getiterator("wireless-network")))
    tenth = total/10
    count = 0
    clients = list()

    for network in doc.getiterator("wireless-network"):
        count += 1
        if (count % tenth) == 0:
            sys.stdout.write(".") # ETA calculation
        type = network.attrib["type"]

        # Channel
        channel = network.find('channel').text
        
        # MAC Address (BSSID)
        bssid = network.find('BSSID').text
        
        # MAC Address details (using Manuf.py)
        macinfo = mac_parser.get_comment(bssid)
        if macinfo is None:
            macinfo = 'N/A'

        # Skip probes or 0 channel
        if type == "probe" or channel == "0":
            continue
        
        # Encryption data parsing
        encryption = network.getiterator('encryption')
        privacy = ""
        cipher = ""
        auth = ""
        if encryption is not None:
            for item in encryption:
                if item.text.startswith("WEP"):
                    privacy = "WEP"
                    cipher = "WEP"
                    auth = ""
                    break
                elif item.text.startswith("WPA"):
                    if item.text.endswith("PSK"):
                        auth = "PSK"
                    elif item.text.endswith("AES-CCM"):
                        cipher = "CCMP " + cipher
                    elif item.text.endswith("TKIP"):
                        cipher += "TKIP "
                elif item.text == "None":
                    privacy = "OPN"

        cipher = cipher.strip()

        if cipher.find("CCMP") > -1:
            privacy = "WPA2"

        if cipher.find("TKIP") > -1:
            privacy += "WPA"

        # Signal strength information
        power = network.find('snr-info')
        dbmmin, dbmmmax = "", ""

        if power is not None:
            dbmmax = power.find('max_signal_dbm').text
            dbmmin = power.find('min_signal_dbm').text

        #if int(dbm) > 1:
        #    dbm = power.find('last_signal_dbm').text

        #if int(dbm) > 1:
        #    dbm = power.find('min_signal_dbm').text

        # ESSID information
        ssid = network.find('SSID')
        essid_text = ""
        if ssid is not None:
            essid_text = network.find('SSID').find('essid').text

        # GPS (LAT/LON) information
        gps = network.find('gps-info')
        lat, lon = '', ''
        if gps is not None:
            lat = network.find('gps-info').find('avg-lat').text
            lon = network.find('gps-info').find('avg-lon').text

        # Date mix/max
        datemin = network.attrib['first-time']
        datemax = network.attrib['last-time']

        # Datasize
        datasize = network.find('datasize').text

        # Clients parsing
        clients_seen = 0
        c_list = associatedClients(network, bssid, essid_text)
        if c_list is not None:
            clients.append(c_list)
            clients_seen = len(c_list)

        # Write results string
        result += '"%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s"\n' % (bssid, macinfo, channel, privacy, cipher, auth, dbmmin, dbmmax, essid_text, clients_seen, datemin, datemax, datasize, lat, lon)

    return result, clients

def associatedClients(network, bssid, essid_text):
    clients = network.getiterator('wireless-client')

    if clients is not None:
        client_info = list()
        for client in clients:
            mac = client.find('client-mac')
            # Kismet shows access point itself as a client, so we remove them
            if mac is not None and mac.text != bssid:
                # Client MAC info
                client_mac = mac.text

                # MAC Address details (using Manuf.py)
                macinfo = mac_parser.get_comment(bssid)
                if macinfo is None:
                    macinfo = 'N/A'

                # Client Power info
                snr = client.find('snr-info')
                if snr is not None:
                    power = client.find('snr-info').find('max_signal_dbm')
                    if power is not None:
                        client_power = power.text
                        c = client_mac, macinfo, client_power, bssid, essid_text
                        client_info.append(c)

        return client_info

if __name__ == "__main__":
    # Start Manuf.py
    mac_parser = manuf.MacParser('/etc/manuf')
    # Start main XML loop
    run(mac_parser)
