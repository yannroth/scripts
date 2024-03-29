# Upscale
This script is to ease and to automatize the process to upscale picture using upscayl.

## Usage
```
usage: upscale.py [-h] [-o OUTPUT_FILE] [-s SCALE] [-m MODEL] [-a] [-v]
                  input_file

convert input to png, upscale it, compress it to jpg

positional arguments:
  input_file            Input pointing to a file or directory with jpg files
                        to upscale.

options:
  -h, --help            show this help message and exit
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        Output file name, can be omited
  -s SCALE, --scale SCALE
                        Scale for upscaling
  -m MODEL, --model MODEL
                        Model to use for upscaling ['realesrgan-x4plus',
                        'remacri', 'ultramix_balanced', 'ultrasharp',
                        '4x_NMKD-Siax_200k', '4xLSDIRplusC']
  -a, --all             Perform upscalling with every model for comparison,
                        this will take a while
  -v, --version         show program's version number and exit
```

## Dependencies
The script uses the command line version of upscayl, [upscayl-nncn](https://github.com/upscayl/upscayl-ncnn). Follow instruction to build or download latest built release.

It also uses Pillow for image conversion, install with

```
pip install pillow
```

You'll also needs the models that are available in [upscayl repo](https://github.com/upscayl/upscayl) under `resources/models`

And also in the [custom-models repo](https://github.com/upscayl/custom-models) under `models`.

Only a chosen subset of models is available in the script, and you'll need to adapt the global variables 
```
__upscayl__ = 'upscayl-bin'
__model_path__ = '/home/yann/git/upscayl/resources/models/'
__custom_model_path__ = '/home/yann/git/custom-models/models/'
```
Depending of your setup.
