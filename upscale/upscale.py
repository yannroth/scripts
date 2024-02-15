#!/usr/bin/python3

import argparse
import os
import glob
from PIL import Image as img
import subprocess

img.MAX_IMAGE_PIXELS = 492000000

__version__ = '0.0.1'
__prog__ = 'upscale'
__name_version__ = __prog__ + ' ' + __version__

__upscayl__ = 'upscayl-bin'
__model_path__ = '/home/yann/git/upscayl/resources/models/'
__custom_model_path__ = '/home/yann/git/custom-models/models/'

models = {
    'realesrgan-x4plus': __model_path__,
    'remacri': __model_path__,
    'ultramix_balanced': __model_path__,
    'ultrasharp': __model_path__,
    '4x_NMKD-Siax_200k': __custom_model_path__,
    '4xLSDIRplusC': __custom_model_path__,
}

class CommandExecutionError(Exception):
    pass

def existing_path(string):
    if not os.path.exists(string):
        raise argparse.ArgumentTypeError(repr(string) + " not found.")
    return os.path.abspath(string)

def convert_jpg_to_png(input_file, output_file=None):
    print(f'Converting {input_file} to png')
    if output_file is None:
        output_file = os.path.splitext(input_file)[0] + '.png'
    
    if input_file.lower().endswith('.png'):
        print(f'Input already a png')
        return input_file

    try:
        image = img.open(input_file)
        image.save(output_file, format="PNG")
        print(f'Saved png as {output_file}')
        return output_file
    except Exception as e:
        print(f'Error during conversion: {e}')
        raise e

def upscale(input_file, output_file=None, scale=4, model_path=__model_path__, model_name='ultrasharp'):
    print(f'Upscaling {input_file}')
    if output_file is None:
        output_file = os.path.splitext(input_file)[0] + '_' + model_name + '_x' + str(scale) + '.png'

    result = subprocess.run([__upscayl__, '-i', input_file, '-s', str(scale), '-m', model_path,
                             '-n', model_name, '-o', output_file],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) 

    if result.returncode == 0:
        print(f'Saved upscaled as {output_file}')
        return output_file
    else:
        error_message = f'Upscale command execution failed with return code {result.returncode}\n'
        error_message += f'STDOUT: {result.stdout}\n'
        error_message += f'STDERR: {result.stderr}'
        raise CommandExecutionError(error_message)

def compress(input_file, output_file=None, quality=50):
    print(f'Compressing {input_file}')
    if output_file is None:
        output_file = os.path.splitext(input_file)[0] + '.jpg'

    image = img.open(input_file)
    image.convert('RGB').save(output_file, 'JPEG', quality=quality)

    print(f'Saved compressed file as {output_file}')
    return output_file

def main(args):
    if os.path.isdir(args.input_file):
        directory = args.input_file
        extensions = ['.jpg', '.JPG', '.jpeg', '.JPEG']
        files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and any(f.endswith(ext) for ext in extensions)]
        print('Files to be processed : ' + str(files))
    else:
        files = [args.input_file]

    for file in files:
        png_file = convert_jpg_to_png(file)
        if args.all:
            for model in models:
                upscaled_file = upscale(png_file, scale=args.scale,
                                      model_name=model,
                                    model_path=models[model])
                compressed_file = compress(upscaled_file, args.output_file)
        else:
            upscaled_file = upscale(png_file, scale=args.scale,
                                    model_name=args.model,
                                   model_path=models[args.model])
            compressed_file = compress(upscaled_file, args.output_file)

def parse_args():
    parser = argparse.ArgumentParser(description='convert input to png, upscale it, compress it to jpg')
    parser.add_argument('input_file', type=existing_path,
                        help='Input pointing to a file or directory with jpg files to upscale.')
    parser.add_argument('-o', '--output_file', default=None,
                        help='Output file name, can be omited')
    parser.add_argument('-s', '--scale', default=4,
                        help='Scale for upscaling')
    parser.add_argument('-m', '--model', default='ultrasharp',
                        help='Model to use for upscaling ' + str([model for model in models]))
    parser.add_argument('-a', '--all', action='store_true',
                        help='Perform upscalling with every model for comparison, this will take a while')
    parser.add_argument('-v', '--version', action='version', version=__name_version__)
    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args = parse_args()
    main(args)
