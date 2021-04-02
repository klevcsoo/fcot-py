import sys
import os
from subprocess import check_output
from shutil import rmtree
from PIL import Image, ImageFilter


# CONFIG
TARGET_WIDTH = 2000
OUTPUT_HEIGHT = 500
WORK_DIR = '.temp'

# CHECKING INPUT ARGUMENT
if len(sys.argv) < 2:
    print('[ERROR] Missing argument: input file')
    exit(1)

# DEFINING INPUT AND OUTPUT
input_path = sys.argv[1]
output_path = sys.argv[2] if len(sys.argv) > 2 else f'{input_path}.png'

# EMPTYING TEMP DIRECTORY
if os.path.isdir(WORK_DIR):
    rmtree(WORK_DIR)
os.makedirs(WORK_DIR)

# CHECKING INPUT FILE EXISTANCE
if not os.path.exists(input_path):
    print('[ERROR] Input file does not exist')
    exit(1)

# GETTING DURATION AND CALCULATING EXTRACTION RATE
duration = float(check_output(f'ffprobe -i {input_path} -show_format -loglevel panic | grep duration', shell=True).decode('UTF-8')[9:])
rate = duration / TARGET_WIDTH

# EXTRACTING FRAMES
print(f'[INFO] Getting a frame every {rate} seconds')
os.system(f'ffmpeg -loglevel fatal -i {input_path} -s 100x100 -r 1/{rate} {WORK_DIR}/frame%03d.bmp')

# COLLECTING EXTRACTED FRAMES, AND SORTING THEM
extracted_files = [f for _, _, f in os.walk(WORK_DIR)][0]
extracted_files.sort()

# CALCULATING THE AVERAGE COLOUR IN EACH OF THE FRAMES
print('[INFO] Calculating colours')
colours = []
for filename in extracted_files:
    img = Image.open(f'{WORK_DIR}/{filename}')
    img.filter(ImageFilter.GaussianBlur(100))
    colours.append(img.getpixel((50, 50)))
    img.close()

# CREATING OUTPUT PICTURE BASED ON COLOUR DATA
actual_width = len(colours)  # should be equal to TARGET_WIDTH, but you never know
out_img = Image.new('RGB', (actual_width, OUTPUT_HEIGHT))
out_img.putdata(colours * OUTPUT_HEIGHT)
out_img.save(output_path)
out_img.close()
print(f'[Info] Done! The path of the output file is {output_path}.')

# REMOVING TEMP DIRECTORY
rmtree(WORK_DIR)
