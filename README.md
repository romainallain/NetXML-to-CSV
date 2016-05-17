# NetXML-to-CSV

Converts Kismet/AirCrack NetXML Wireless logs to a CSV format.

Based on https://github.com/Meatballs1/NetXML-to-CSV
Manuf.py comes from https://github.com/coolbho3k/manuf.py

## Setup
```bash
cp manuf /etc/
```
It may be useful to follow the "Maintenance" step before, to update this file.

## Usage
```
Usage: python netxml_to_csv.py INPUT OUTPUTBASENAME
```

INPUT must be a .netxml file.
OUTPUTBASENAME will be used to create 2 output files:
  * OUTPUTBASENAME_ap.csv which contains info on access points
  * OUTPUTBASENAME_clients.csv which contains info on clients detected during tapping

Exemple usage:
```
python netxml_to_csv.py Kismet-20160507-23-12-40-1.netxml WifiAudit
```
will create WifiAudit_ap.csv and WifiAudit_clients.csv

## Maintenance
To update "manuf" file:
```bash
wget -O manuf "https://code.wireshark.org/review/gitweb?p=wireshark.git;a=blob_plain;f=manuf"
```
