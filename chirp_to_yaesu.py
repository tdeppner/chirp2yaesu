#!/usr/bin/env python

import csv
import argparse

class Radio:
    def __init__(self, name, channels, emptylinefmt):
        self.name = name
        self.channels = int(channels)
        self.emptylinefmt = emptylinefmt
        self.fields = []
        self.default_dict = {}
        return

    def get_dict(self):
        new_dict = dict((x, self.default_dict.get(x, '')) for x in self.fields)
        return new_dict


FTM400 = Radio(name='FTM-400', channels=500, emptylinefmt=',,,,,,,,,,,,,,0,,0')
FTM400.fields = [
    'Location', 'RX Frequency', 'TX Frequency', 'Offset', 'Duplex', 'Mode', 'Name', 'Tone', 'rToneFreq', 'DtcsCode',
    'UnkOne', 'UnkTwo', 'UnkThree', 'Width', 'UnkFour', 'Comment', 'Band']
FTM400.default_dict = dict(UnkFour=0, Band=0, NothingAtAll='zesty')


def addEmptyLine(foo, lineNumber):
    templine = str(lineNumber) + FTM400.emptylinefmt
    foo.append(templine.split(","))
    return foo

# Adding the command line flags
parser = argparse.ArgumentParser(description="This tool converts a chirp csv file to a Yaesu importable csv file.")
parser.add_argument('--input', '-i', required = True)
parser.add_argument('--output', '-o', default="Yaesu-import.csv")
parser.add_argument('--band', '-b', default='A', choices = ['A', 'B'], help='Specify the A or B band, only for FTM-400')
args = parser.parse_args()

ftline = []
chirpFile = []
outlist = []
numlines = 0
inputFile = args.input
outputFile = args.output
if args.band == 'A':
    band = "0"
else :
    band = "1"

radio = FTM400

# Open the Chirp file and create the Yaesu formatted array
with open(inputFile) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row["Location"] == "0":
            continue
        while numlines + 1 != int(row["Location"]):
            numlines += 1
            chirpFile = addEmptyLine(chirpFile, numlines)
            outdict = radio.get_dict()
            outdict['Location'] = numlines
            outlist.append(outdict)

        outdict = radio.get_dict()

        if row["Tone"] in ("Tone", "TSQL") or (row['Frequency'] != None and row["Tone"] == ''):
            numlines += 1
            ftline.append(str(numlines))
            outdict['Location'] = str(numlines)
            ftline.append(row['Frequency'])
            outdict['RX Frequency'] = row['Frequency']
            if row['Offset'] == "OFF":
                ftline.append(row['Frequency'])
                outdict['TX Frequency'] = row['Frequency']
            else :
                freq = float( row['Frequency'] )
                if row['Duplex'] == "-" :
                    freq = freq - float( row['Offset'] )
                elif row['Duplex'] == "+":
                    freq = freq + float( row['Offset'] )
                ftline.append(str(freq))
                outdict['TX Frequency'] = str(freq)
            ftline.append(row['Offset'])
            outdict['Offset'] = row['Offset']
            if row['Duplex'] in [ '+', '-' ] :
                ftline.append(row['Duplex'] + "RPT")
                outdict['Duplex'] = row['Duplex'] + 'RPT'
            else :
                ftline.append( "OFF" )
                outdict['Duplex'] = 'OFF' # make the default ? @@
            ftline.append(row['Mode'])
            outdict['Mode'] = row['Mode']
            ftline.append(row['Name'][0:8])
            outdict['Name'] = row['Name'][0:8]
            if row["Tone"] == "Tone" :
                ftline.append("TONE ENC")
                outdict['Tone'] = 'TONE ENC'
            elif row["Tone"] == "TSQL" :
                ftline.append("TONE SQL")
                outdict['Tone'] = 'TONE SQL'
            else :
                ftline.append("OFF")
                outdict['Tone'] = 'OFF' # make the default ? @@
            ftline.append(row['rToneFreq'] + " Hz")
            outdict['rToneFreq'] = row['rToneFreq'] + ' Hz'
            ftline.append(row['DtcsCode'])
            outdict['DtcsCode'] = row['DtcsCode']
            ftline.append("1500 Hz")
            outdict['UnkOne'] = '1500 Hz'
            ftline.append("HIGH")
            outdict['UnkTwo'] = 'HIGH'
            ftline.append("OFF")
            outdict['UnkThree'] = 'OFF'
            if row['Mode'] == "NFM":
                ftline.append("12.5KHz")
                outdict['Width'] = '12.5KHz'
            else :
                ftline.append("25.0KHz")
                outdict['Width'] = '25.0KHz'
            ftline.append("0")
            ftline.append(row['Comment'])
            ftline.append(band)

            chirpFile.append(ftline)
            outlist.append(outdict)
            ftline = []
        else:
            # If it's not Tone, Don't do anything now, just add an empty line
            # This will have to handle DCS stuff one day.
            numlines += 1
            chirpFile = addEmptyLine(chirpFile, numlines)

# For some reason Yaesu import CSV file expects 500 lines,
# filling the rest with empty lines here

for line in range(numlines+1, FTM400.channels + 1):
    chirpFile = addEmptyLine(chirpFile, line)
    outdict = radio.get_dict()
    outdict['Location'] = line
    outlist.append(outdict)

# Writing the file to Yaesu importable CSV file.
with open(outputFile, "w") as csvWriter:
    writer = csv.writer(csvWriter, delimiter=",")
    for line in chirpFile:
        writer.writerow(line)

with open(outputFile, 'w') as csvWriter:
    writer = csv.DictWriter(csvWriter, fieldnames=radio.fields, delimiter=',')
    for adict in outlist:
        writer.writerow(adict)