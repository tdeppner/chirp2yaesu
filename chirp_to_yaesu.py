#!/usr/bin/env python

import csv
import argparse


class Radio:
    """Detail required to build a CSV output record for the given device."""

    def __init__(self, name, channels=None, write_header=False):
        self.name = name
        self.channels = None
        if channels is not None:
            self.channels = int(channels)
        self.fields = []
        self.channel_dict = {}
        self.empty_channel_dict = {}
        self.write_header = write_header
        return

    def build_channel_dict(self, adict=None):
        """Return a dict for a defined channel, also can be used to constrain the input adict to the radio's fields."""
        if adict is None:
            adict = self.empty_channel_dict | self.channel_dict
        return dict((x, adict.get(x, '')) for x in self.fields)

    def build_empty_channel_dict(self):
        """Return a dict suitable for an empty row in the output CSV."""
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

CHIRP = Radio(name='CHIRP', channels=None, write_header=True)
CHIRP.set_fields_list([
    'Location', 'Name', 'Frequency', 'Duplex', 'Offset', 'Tone', 'rToneFreq', 'cToneFreq', 'DtcsCode', 'DtcsPolarity',
    'Mode', 'TStep', 'Skip', 'Comment', 'URCALL', 'RPT1CALL', 'RPT2CALL', 'DVCODE'
])
CHIRP.update_channel_dict({
    'cToneFreq': '88.5',
    'TStep': '5.00',
    'DtcsPolarity': 'NN'
})

RADIOS = [FT70, FTM300, FTM400, FTM500, CHIRP]
for radio in RADIOS:
    if radio in (FT70, FTM300, FTM400, FTM500):
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

FREQUENCY_IS_YAESU_SET = set(
    ['RX Frequency', 'TX Frequency', 'Offset', 'Duplex'])


def xlat_frequency(incoming, radio):
    """Translate Frequency details from incoming format to outgoing format, return a new dict with the specifics.

    Currently, we presume that incoming is always Chirp style (Frequency, Duplex, Offset). This will change.

    @@ gives no output if no radio is matched
    """
    outdict = {}

    # Consider outgoing format needs and build outdict
    if radio in (FT70, FTM300, FTM400, FTM500):
        outdict['RX Frequency'] = incoming['Frequency']
        outdict['Offset'] = incoming['Offset']
        if incoming['Offset'] == 'OFF':
            outdict['TX Frequency'] = incoming['Frequency']
        else:
            freq = float(incoming['Frequency'])
            if incoming['Duplex'] == '-':
                freq = freq - float(incoming['Offset'])
            elif incoming['Duplex'] == "+":
                freq = freq + float(incoming['Offset'])
            outdict['TX Frequency'] = '{:0.6f}'.format(freq)
        if incoming['Duplex'] in ['+', '-']:
            outdict['Duplex'] = incoming['Duplex'] + 'RPT'
    elif radio == CHIRP and FREQUENCY_IS_YAESU_SET.issubset(set(incoming)):
        outdict['Frequency'] = incoming['RX Frequency']
        outdict['Offset'] = incoming['Offset']
        if incoming['Duplex'] == 'OFF':
            outdict['Duplex'] = ''
        else:
            outdict['Duplex'] = incoming['Duplex'][0:1]

    return outdict


def xlat_mode(incoming, radio):
    """Translate Mode details from incoming format to outgoing format, return a new dict with the specifics.

    Currently, we presume that incoming is always Chirp style (Mode). This will change.
    """
    outdict = {}

    # Consider outgoing format needs and build outdict
    if radio in (FT70, FTM300, FTM500):
        if incoming['Mode'] == 'NFM':
            outdict['Mode'] = 'FM'

    if radio == FTM400:
        if incoming['Mode'] == 'NFM':
            outdict['Width'] = '12.5KHz'
        else:
            outdict['Width'] = '25.0KHz'
    elif radio in (FTM300, FTM500):
        if incoming['Mode'] == 'NFM':
            outdict['Narrow'] = 'ON'
        else:
            outdict['Narrow'] = 'OFF'

    if radio == CHIRP:
        if 'Width' in incoming and incoming['Width'] == '12.5Khz':
            outdict['Mode'] = 'NFM'
        elif 'Narrow' in incoming and incoming['Narrow'] == 'ON':
            outdict['Mode'] = 'NFM'

    for key in ('Mode', ):
        if key not in outdict:
            outdict[key] = incoming[key]

    return outdict


def xlat_tone(incoming, radio):
    """Translate Tone details from incoming format to outgoing format, return a new dict with the specifics.

    Currently, we presume that incoming is always Chirp style (Mode). This will change.

    @@ gives no output if no radio is matched
    """
    outdict = {}

    if radio in (FT70, FTM300, FTM400, FTM500):
        if incoming['Tone'] == 'Tone':
            if radio == FTM400:
                outdict['Tone'] = 'TONE ENC'
            else:
                outdict['Tone'] = 'TONE'
        elif incoming['Tone'] == 'TSQL':
            outdict['Tone'] = 'TONE SQL'
        outdict['rToneFreq'] = incoming['rToneFreq'] + ' Hz'
    elif radio == CHIRP:
        if incoming['Tone'] in ('TONE', 'TONE ENC'):
            outdict['Tone'] = 'Tone'
        elif incoming['Tone'] == 'TONE SQL':
            outdict['Tone'] = 'TSQL'
        elif incoming['Tone'] == 'OFF':
            outdict['Tone'] = ''
        if ' Hz' in incoming['rToneFreq']:
            outdict['rToneFreq'] = incoming['rToneFreq'].partition(' ')[0]

        for key in ('Tone', 'rToneFreq'):
            if key not in outdict:
                outdict[key] = incoming[key]
        if outdict['Tone'] == 'TSQL':
            outdict['cToneFreq'] = outdict['rToneFreq']

    return outdict


def parse_args():
    parser = argparse.ArgumentParser(
        description="This tool converts a chirp csv file to a Yaesu importable csv file.")
    parser.add_argument('--input', '-i', required=True)
    parser.add_argument('--output', '-o', default="Yaesu-import.csv")
    parser.add_argument('--radio', '-r', default=FTM400.name, choices=[
                        FT70.name, FTM300.name, FTM400.name, FTM500.name, CHIRP.name], help='Specify radio model [' + FTM400.name + ']')
    parser.add_argument('--band', '-b', default='A',
                        choices=['A', 'B'], help='Specify the [A] or B band, only for FTM-400')
    parser.add_argument('--format', '-f', default=CHIRP.name, choices=[
                        FT70.name, FTM300.name, FTM400.name, FTM500.name, CHIRP.name], help='Specify input CSV format.')
    return parser.parse_args()


def output_csv(args):
    outlist = []
    numlines = 0
    inputFile = args.input
    outputFile = args.output
    band = 0
    if args.radio == FTM400.name and args.band == 'B':
        band = "1"

    for radio in RADIOS:
        if args.radio == radio.name:
            break

    for csvformat in RADIOS:
        if args.format == csvformat.name:
            break

    def addEmptyLine(lineNumber, band=0):
        outdict = radio.build_empty_channel_dict()
        outdict['Location'] = lineNumber
        outdict['Band'] = band
        outlist.append(outdict)

    # Open the Chirp file and create the Yaesu formatted array
    with open(inputFile) as csvfile:
        fieldnames = None
        if args.format is not CHIRP.name:
            fieldnames = csvformat.fields
        reader = csv.DictReader(csvfile, fieldnames)
        for row in reader:
            if row['Location'] == '0':
                continue
            while numlines + 1 != int(row['Location']):
                numlines += 1
                if radio.channels:
                    addEmptyLine(numlines, band=band)

            outdict = radio.build_channel_dict()

            # xlat incoming data formats
            row |= xlat_frequency(row, CHIRP)
            row |= xlat_mode(row, CHIRP)
            row |= xlat_tone(row, CHIRP)

            if row['Frequency'] and row['Tone'] in ('', 'Tone', 'TSQL'):
                numlines += 1
                outdict['Location'] = str(numlines)
                outdict['Band'] = band
                outdict['Name'] = row['Name'][0:8]
                outdict['Comment'] = row['Comment']
                outdict['DtcsCode'] = row['DtcsCode']

                outdict |= xlat_frequency(row, radio)
                outdict |= xlat_mode(row, radio)
                outdict |= xlat_tone(row, radio)

                outdict = radio.build_channel_dict(outdict)
                outlist.append(outdict)

            else:
                # If it's not Tone, Don't do anything now, just add an empty line
                # This will have to handle DCS stuff one day.
                numlines += 1
                if radio.channels:
                    addEmptyLine(numlines, band=band)

    if radio.channels:
        for line in range(numlines+1, radio.channels + 1):
            addEmptyLine(line, band=band)

    with open(outputFile, 'w') as csvWriter:
        writer = csv.DictWriter(
            csvWriter, fieldnames=radio.fields, delimiter=',')
        if radio.write_header:
            writer.writeheader()
        for n, adict in enumerate(outlist):
            if radio.channels and n + 1 > radio.channels:
                print('too many input channels for the {}, stopping at {}. (not a problem during testing)'.format(
                    radio.name, radio.channels))
                break
            writer.writerow(adict)


def main():
    args = parse_args()
    output_csv(args)


if __name__ == '__main__':
    main()
