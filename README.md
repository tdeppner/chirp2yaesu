This code converts CSV export files from various software and radio formats. It
was originally designed to support Chirp export file in CSV format to Yaesu's
import CSV format for the FTM400.

Use this code at your own discretion. It's not tested on all Yaesu programs.
# Supported software and radios
- Chirp (~2024)
- The following Yaesu radios via their specific ADMS Software
  - FT70
  - FTM300
  - FTM400
  - FTM500

# HOW - From Scratch

1. Download Chirp and create a station list.
2. Export this station as a CSV file. (You can name it Chirp-export.csv)
3. Download the chirp2yaesu package from github.com
4. Run it as: python chirp_to_yaesu.py -o Yaesu-import.csv -i Chirp-export.csv
5. Use Yaesu-import.csv file to import the configuration in the Yaesu's own software.

# HOW - From a radio you already have
1. Use the source radios programming software to read the radio and export a CSV file.
  - For Yaesu ADMS software this means:
    - Plug in a blank SD Card to the radio
      - Use the radio's menus to write the config to the SD Card
    - Load the ADMS software for that radio
      - Read from the SD Card
      - Export the CSV file (consider doing this for each bank if using the FTM 400, if desired)
2. Run this software as:
  - python chirp_to_yaesu.py -i input_filename.csv -o output_filename.csv -f SOURCE_FORMAT -r OUTPUT_FORMAT
  - adjust the filenames and FORMATs as desired
3. Use the target radios programming software to write the radio from an imported CSV file.
  - For Yaesu ADMS software this means:
    - Ensure you have an SD Card that has been written to by your target radio (i.e. from Step 1)
    - Load the ADMS software for that radio
      - Read from the SD Card for the radio
      - Import the CSV file output from chirp_to_yaesu.py above
      - Write the configuration to the SD Card
    - Place the SD Card into the radio
      - Use the radio's menus to read the config from the SD Card

Hopefully it's obvious, but you could take a CHIRP formatted CSV into Chirp, use it to edit your channel lists more easily, then export from Chirp and import back into your radio.

# Things to Note

This software is only translating between CSV formats. It does not directly configure any radio, rather you'll need specific radio programming software (i.e. Yaesu ADMS, Chirp, etc).

If you have a different format and would like help with a tranlation, or want support for a different radio or software, consider filing an issue or a pull request. We will need a copy of a sample CSV file for testing and confirmation.

We're currently working on a test suite.

It'd be good to add support for RT Systems CSV exports. If you have examples of such, please send them along.

CSV stands for Comma Separated Values, and is simply a text file with some special formatting rules. Those rules vary between different systems, thus this code exists to massage data between these formats.

# SCREENSHOTS

Chirp Export

![Chirp Export](http://i.imgur.com/kPHwyOal.png)

# TODO

- So far only Tone and Tone SQL mode are supported, add DTCS, etc...
- Better error handling

# SOFAR

- Fixed a problem with enabling Tone SQL mode. (TONE ENC)
- Added basic argument parsing
- Better code commenting
- Add better csv writing
- Added Tone SQL support
- Now retains "holes" in the incoming CSV, retains CSV location numbers
- Will skip any location "0" entries, ie anomolous Chirp CSV export from some radios.
