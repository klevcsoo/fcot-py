import sys
import os
from subprocess import check_output
from shutil import rmtree
from PIL import Image, ImageFilter


TARGET_WIDTH = 2000
OUTPUT_HEIGHT = 500

if len(sys.argv) < 2:
    print('[ERROR] Missing argument: input file')
    exit(1)

input_path = sys.argv[1]
output_path = sys.argv[2] if len(sys.argv) > 2 else f'{input_path}.png'

if os.path.isdir('temp'):
    rmtree('temp')
os.makedirs('temp')

if not os.path.exists(input_path):
    print('[ERROR] Input file does not exist')
    exit(1)

duration = float(check_output(f'ffprobe -i {input_path} -show_format -loglevel panic | grep duration', shell=True).decode('UTF-8')[9:])
rate = duration / TARGET_WIDTH

print(f'[INFO] Getting a frame every {rate} seconds')
os.system(f'ffmpeg -loglevel fatal -i {input_path} -s 100x100 -r 1/{rate} temp/frame%03d.bmp')

extracted_files = [f for _, _, f in os.walk('temp')][0]
extracted_files.sort()

colours = []
for filename in extracted_files:
    img = Image.open(f'temp/{filename}')
    img.filter(ImageFilter.GaussianBlur(100))
    colours.append(img.getpixel((50, 50)))
    img.close()

actual_width = len(colours)  # should be equal to TARGET_WIDTH, but you never know
out_img = Image.new('RGB', (actual_width, OUTPUT_HEIGHT))
out_img.putdata(colours * OUTPUT_HEIGHT)
out_img.save(output_path)
out_img.close()
