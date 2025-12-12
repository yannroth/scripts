# RencodeFlac

This script is to try to uncorrupt flac file by decoding them and re-encoding them with the latest flac library. The binary for flac version 1.2.1 has this older version can be used to decode with this less restrictive version of the lib.

```
usage: rencodeFlac.py [-h] [-i INPUT] [-o OUTPUT] [--flac-bin FLAC_BIN] [--decoder-bin DECODER_BIN]

Batch decode+re-encode FLACs, continuing past corruption.

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input directory containing FLAC files (default: current directory)
  -o OUTPUT, --output OUTPUT
                        Output directory for re-encoded FLAC files (default: re-encode)
  --flac-bin FLAC_BIN   Path to flac binary (default: system 'flac')
  --decoder-bin DECODER_BIN
                        FLAC binary used for decoding (default: system 'flac')

Usage examples:
    To decode using the flac v.1.2.1 binary:
        python rencodeFlac.py -i flac_folder --decoder-bin ../flac121/bin/flac
            
    To simply decode and re-encode flac in current folder:
        python rencodeFlac.py
```
