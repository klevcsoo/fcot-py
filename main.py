import sys
import os
import time
import datetime
import multiprocessing
import progressbar
from subprocess import check_output
from shutil import rmtree
from PIL import Image, ImageFilter


# CONFIG
TARGET_WIDTH = 2000
OUTPUT_HEIGHT = 500
WORK_DIR = '.temp'


# ✨FANCY✨ CONSOLE OUTPUT COLOURS
class OutColours:
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    END = '\033[0m'


# CHECKING INPUT ARGUMENT
if len(sys.argv) < 2:
    print(f'{OutColours.ERROR}[ERROR] Missing argument: input file{OutColours.END}')
    exit(1)

# DEFINING INPUT AND OUTPUT
input_path = sys.argv[1]
output_path = sys.argv[2] if len(sys.argv) > 2 else f'{input_path}.png'

# EMPTYING TEMP DIRECTORY
if os.path.isdir(WORK_DIR):
    rmtree(WORK_DIR)
os.makedirs(WORK_DIR)

# CHECKING INPUT FILE EXISTENCE
if not os.path.exists(input_path):
    print(f'{OutColours.ERROR}[ERROR] Input file does not exist{OutColours.END}')
    exit(1)
print(f'[INFO] Input file: {input_path}')

# GETTING DURATION AND CALCULATING EXTRACTION RATE
duration_cmd = f'ffprobe -i {input_path} -show_format -loglevel panic | grep duration'
duration = float(check_output(duration_cmd, shell=True).decode('UTF-8')[9:])
rate = duration / TARGET_WIDTH


# WATCHING WORK DIRECTORY TO UPDATE PROGRESS ----
# I don't fully understand why it has to be like this,
# but it does work this way
def update_progress(start_time: float, pbar=progressbar.ProgressBar):
    try:
        while True:
            seconds_done = len([f for _, _, f in os.walk(WORK_DIR)][0]) * rate
            percentage = round(100 * (seconds_done / duration), 1)
            pbar.update(percentage)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print(f'{OutColours.WARNING}\n[WARN] Extraction aborted{OutColours.END}')


start_time = time.time()
print('[INFO] Extracting frames...')
epbar = progressbar.ProgressBar(maxval=100).start()
if sys.platform == 'darwin':
    multiprocessing.set_start_method('fork')
progress_update_thread = multiprocessing.Process(target=update_progress, args=[start_time, epbar])
try:
    progress_update_thread.start()
except RuntimeError:
    try:
        progress_update_thread.terminate()
    except AttributeError:
        pass
    except Exception as e:
        print(f'{OutColours.ERROR}[ERROR] Runtime error: {e}{OutColours.END}')
except Exception as e:
    print(f'{OutColours.ERROR}[ERROR] Runtime error: {e}{OutColours.END}')

# -----------------------------------------------

# EXTRACTING FRAMES
ext_cmd = f'ffmpeg -loglevel fatal -i {input_path} -s 100x100 -r 1/{rate} {WORK_DIR}/frame%03d.bmp'
ext_cmd_return_val = os.system(ext_cmd)
work_time = round(time.time() - start_time)

# STOP PROGRESS LOGGING PROCESS
progress_update_thread.terminate()
if ext_cmd_return_val == 0:
    epbar.finish()
else:
    exit(0)

# COLLECTING EXTRACTED FRAMES, AND SORTING THEM
extracted_files = [f for _, _, f in os.walk(WORK_DIR)][0]
extracted_files.sort()

# CALCULATING THE AVERAGE COLOUR IN EACH OF THE FRAMES
print('[INFO] Calculating colours...')
cpbar = progressbar.ProgressBar(maxval=100).start()
colours = []
for filename in extracted_files:
    img = Image.open(f'{WORK_DIR}/{filename}')
    img.filter(ImageFilter.GaussianBlur(100))
    colours.append(img.getpixel((50, 50)))
    img.close()

    percentage = int((len(colours) / len(extracted_files)) * 100)
    cpbar.update(percentage)
cpbar.finish()

# CREATING OUTPUT PICTURE BASED ON COLOUR DATA
actual_width = len(colours)  # should be equal to TARGET_WIDTH, but you never know
out_img = Image.new('RGB', (actual_width, OUTPUT_HEIGHT))
out_img.putdata(colours * OUTPUT_HEIGHT)
out_img.save(output_path)
out_img.close()
print(f'[INFO] Done! Work time: {str(datetime.timedelta(seconds=work_time))}')
print(f'[INFO] Output file: {output_path}')

# REMOVING TEMP DIRECTORY
rmtree(WORK_DIR, ignore_errors=True)
