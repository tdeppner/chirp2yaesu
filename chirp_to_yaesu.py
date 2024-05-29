#!/usr/bin/env python

import csv
import argparse


class Radio:
    """Detail required to build a CSV output record for the given device."""

    def __init__(self, name, channels):
        self.name = name
        self.channels = int(channels)
        self.fields = []
        self.channel_dict = {}
        self.empty_channel_dict = {}
        return

    def build_channel_dict(self, adict=None):
        if adict is None:
            adict = self.empty_channel_dict | self.channel_dict
        return dict((x, adict.get(x, '')) for x in self.fields)

    def build_empty_channel_dict(self):
        return self.build_channel_dict(self.empty_channel_dict)

    def set_fields_list(self, alist):
        """Set the fields list to the given input.

        This defines the CSV output specification.
        """
        self.fields = list()
        self.fields.extend(alist)

    def update_channel_dict(self, adict=None):
        """Update common fields for populated CSV records."""
        for key, value in adict.items():
            self.channel_dict[key] = value

    def update_empty_channel_dict(self, adict=None):
        """Update common fields for all CSV records."""
        for key, value in adict.items():
            self.empty_channel_dict[key] = value


FT70 = Radio(name='FT70', channels=900)
FT70.set_fields_list([
    'Location', 'Priority CH', 'RX Frequency', 'TX Frequency', 'Offset', 'Duplex', 'Auto Mode', 'Mode', 'AMS',
    'DigAnalog', 'Name', 'Tone', 'rToneFreq', 'DtcsCode', 'DCS Polarity', 'User CTCSS', 'TX Power', 'Skip', 'Auto Step',
    'Step', 'Tag', 'Memory Mask', 'ATT', 'SMeter SQL', 'Bell', 'Half Dev', 'Clock Shift',
    'Bank1', 'Bank2', 'Bank3', 'Bank4', 'Bank5', 'Bank6', 'Bank7', 'Bank8', 'Bank9', 'Bank10',
    'Bank11', 'Bank12', 'Bank13', 'Bank14', 'Bank15', 'Bank16', 'Bank17', 'Bank18', 'Bank19', 'Bank20',
    'Bank21', 'Bank22', 'Bank23', 'Bank24', 'Comment', 'Band'
])
FT70.update_channel_dict({
    'Priority CH': 'OFF',
    'Auto Mode': 'ON',
    'AMS': 'ON',
    'DCS Polarity': 'RX Normal TX Normal',
    'Skip': 'OFF',
    'Auto Step': 'ON',
    'Tag': 'OFF',
    'Memory Mask': 'OFF',
    'ATT': 'OFF',
    'SMeter SQL': 'OFF',
    'Bell': 'OFF',
    'Half Dev': 'OFF',
    'Clock Shift': 'OFF',
    'DigAnalog': 'ANALOG'
})
for i in range(1, 25):
    key = 'Bank{}'.format(i)
    FT70.update_channel_dict({key: 'OFF'})

FTM300 = Radio(name='FTM300', channels=999)
FTM300.set_fields_list([
    'Location', 'RX Frequency', 'TX Frequency', 'Offset', 'Duplex', 'Mode', 'DigAnalog',
    'Name', 'Tone', 'rToneFreq', 'DtcsCode', 'User CTCSS', 'RX DGID', 'TX DGID', 'TX Power',
    'M-GRP', 'Scan', 'Step', 'Narrow', 'Clock Shift', 'Comment', 'Band'])
FTM300.update_channel_dict({
    'DigAnalog': 'AMS'
})

FTM400 = Radio(name='FTM400', channels=500)
FTM400.set_fields_list([
    'Location', 'RX Frequency', 'TX Frequency', 'Offset', 'Duplex', 'Mode', 'Name', 'Tone', 'rToneFreq', 'DtcsCode',
    'User CTCSS', 'TX Power', 'UnkThree', 'Width', 'UnkFour', 'Comment', 'Band'])
FTM400.update_empty_channel_dict(dict(UnkFour=0, Band=0))
FTM400.update_channel_dict(dict(UnkThree='OFF'))

FTM500 = Radio(name='FTM500', channels=999)
FTM500.set_fields_list([
    'Location', 'RX Frequency', 'TX Frequency', 'Offset', 'Duplex', 'Mode', 'DigAnalog',
    'Name', 'Tone', 'rToneFreq', 'DtcsCode', 'User CTCSS', 'RX DGID', 'TX DGID', 'TX Power',
    'Scan', 'Step', 'Narrow', 'Clock Shift', 'Comment', 'Band'])
FTM500.update_channel_dict({
    'DigAnalog': 'AMS'
})

RADIOS = [FT70, FTM300, FTM400, FTM500]
for radio in RADIOS:
    radio.update_channel_dict({
        'Tone': 'OFF',
        'Duplex': 'OFF',
        'User CTCSS': '1500 Hz',
        'TX Power': 'HIGH',
        'RX DGID': 'RX 00',
        'TX DGID': 'TX 00',
        'M-GRP': 'OFF',
        'Scan': 'YES',
        'Step': '5.0KHz',
        'Clock Shift': 'OFF'
    })


def parse_args():
    parser = argparse.ArgumentParser(
        description="This tool converts a chirp csv file to a Yaesu importable csv file.")
    parser.add_argument('--input', '-i', required=True)
    parser.add_argument('--output', '-o', default="Yaesu-import.csv")
    parser.add_argument('--radio', '-r', default='FTM400', choices=[
                        'FT70', 'FTM300', 'FTM400', 'FTM500'], help='Specify radio model [FTM400]')
    parser.add_argument('--band', '-b', default='A',
                        choices=['A', 'B'], help='Specify the [A] or B band, only for FTM-400')
    return parser.parse_args()


def output_csv(args):
    outlist = []
    numlines = 0
    inputFile = args.input
    outputFile = args.output
    band = 0
    if args.radio == 'FTM400' and args.band == 'B':
        band = "1"

    for radio in RADIOS:
        if args.radio == radio.name:
            break

    def addEmptyLine(lineNumber, band=0):
        outdict = radio.build_empty_channel_dict()
        outdict['Location'] = lineNumber
        outdict['Band'] = band
        outlist.append(outdict)

    # Open the Chirp file and create the Yaesu formatted array
    with open(inputFile) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["Location"] == "0":
                continue
            while numlines + 1 != int(row["Location"]):
                numlines += 1
                addEmptyLine(numlines, band=band)

            outdict = radio.build_channel_dict()

            if row["Tone"] in ("Tone", "TSQL") or (row['Frequency'] != None and row["Tone"] == ''):
                numlines += 1
                outdict['Location'] = str(numlines)
                outdict['RX Frequency'] = row['Frequency']
                if row['Offset'] == "OFF":
                    outdict['TX Frequency'] = row['Frequency']
                else:
                    freq = float(row['Frequency'])
                    if row['Duplex'] == "-":
                        freq = freq - float(row['Offset'])
                    elif row['Duplex'] == "+":
                        freq = freq + float(row['Offset'])
                    outdict['TX Frequency'] = '{:0.6f}'.format(freq)
                outdict['Offset'] = row['Offset']
                if row['Duplex'] in ['+', '-']:
                    outdict['Duplex'] = row['Duplex'] + 'RPT'
                outdict['Mode'] = row['Mode']
                if radio.name in ('FT70', 'FTM300', 'FTM500') and outdict['Mode'] == 'NFM':
                    outdict['Mode'] = 'FM'
                outdict['Name'] = row['Name'][0:8]
                if row["Tone"] == "Tone":
                    # FTM300, FT70
                    outdict['Tone'] = 'TONE ENC' if radio.name == 'FTM400' else 'TONE'
                elif row["Tone"] == "TSQL":
                    outdict['Tone'] = 'TONE SQL'
                outdict['rToneFreq'] = row['rToneFreq'] + ' Hz'
                outdict['DtcsCode'] = row['DtcsCode']
                outdict['Width'] = '12.5KHz' if row['Mode'] == 'NFM' else '25.0KHz'
                outdict['Narrow'] = 'ON' if row['Mode'] == 'NFM' else 'OFF'
                outdict['Comment'] = row['Comment']
                outdict['Band'] = band

                outlist.append(radio.build_channel_dict(outdict))
                # @@ outlist.append(outdict)

            else:
                # If it's not Tone, Don't do anything now, just add an empty line
                # This will have to handle DCS stuff one day.
                numlines += 1
                addEmptyLine(numlines, band=band)

    for line in range(numlines+1, radio.channels + 1):
        addEmptyLine(line, band=band)

    with open(outputFile, 'w') as csvWriter:
        writer = csv.DictWriter(
            csvWriter, fieldnames=radio.fields, delimiter=',')
        for adict in outlist:
            writer.writerow(adict)


def main():
    args = parse_args()
    output_csv(args)


if __name__ == '__main__':
    main()
