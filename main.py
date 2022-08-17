from ntpath import join
import sys
import os
import time
import datetime
from multiprocessing import Pool, Process, set_start_method, get_start_method
from progressbar import ProgressBar
from subprocess import check_output
from shutil import rmtree
from PIL import Image, ImageFilter


# CONFIG
TARGET_WIDTH = 2000
OUTPUT_HEIGHT = 500
WORK_DIR = '.temp'


class OutColours:
    """✨Fancy✨ console output colours."""

    WARNING = '\033[93m'
    ERROR = '\033[91m'
    END = '\033[0m'


def count_files(dir_path: os.PathLike):
    """Returns the number of files inside a folder."""
    return len([f for _, _, f in os.walk(dir_path)][0])


def read_files(dir_path: os.PathLike) -> list[os.PathLike]:
    """Returns the absolute paths of the files in a folder."""
    a = [[[d]*len(f), f] for d, _, f in os.walk('testdir')][0]
    b = [os.path.abspath(f'{a[0][p]}/{a[1][p]}') for p in range(len(a[1]))]
    b.sort()
    return b


def update_progress(pbar: ProgressBar, duration: float, rate: float, work_dir: os.PathLike):
    """Watching directory for progress updates."""
    try:
        while True:
            seconds_done = count_files(work_dir) * rate
            percentage = round(100 * (seconds_done / duration), 1)
            pbar.update(percentage)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print(f'{OutColours.WARNING}\n[WARN] Extraction aborted{OutColours.END}')


def process_video_file(file_path: os.PathLike) -> tuple[Image.Image, str]:
    """Processes a video file, and returns the generated
    image along with the output path."""

    file_basename = os.path.basename(file_path)
    work_dir = f'{WORK_DIR}/{file_basename}'
    if not os.path.isdir(work_dir):
        os.makedirs(work_dir)

    # GETTING DURATION AND CALCULATING EXTRACTION RATE
    duration_cmd = f'ffprobe -i {file_path} -show_format -loglevel panic | grep duration'
    duration = float(check_output(duration_cmd, shell=True).decode('UTF-8')[9:])
    rate = duration / TARGET_WIDTH

    # STARTING EXTRACTION PROGRESS WATCHER
    start_time = time.time()
    print('[INFO] Extracting frames...')
    epbar = ProgressBar(maxval=100).start()
    progress_update_thread = Process(target=update_progress, args=[
        epbar, duration, rate, work_dir
    ])
    try:
        progress_update_thread.start()
    except RuntimeError:
        try:
            progress_update_thread.terminate()
        except AttributeError:
            pass
        except Exception as e:
            print(f'{OutColours.ERROR}[ERROR] Watcher process runtime error: {e}{OutColours.END}')

    # EXTRACTING FRAMES
    c = f'ffmpeg -loglevel fatal -i {file_path} -s 100x100 -r 1/{rate} {work_dir}/frame%03d.bmp'
    ext_cmd_return_val = os.system(c)
    work_time = round(time.time() - start_time)

    # STOP PROGRESS LOGGING PROCESS
    progress_update_thread.terminate()
    if ext_cmd_return_val == 0:
        epbar.finish()
    else:
        raise Exception("Extraction aborted")

    # COLLECTING EXTRACTED FRAMES
    extracted_files = read_files(work_dir)

    # CALCULATING THE AVERAGE COLOUR IN EACH OF THE FRAMES
    print('[INFO] Calculating colours...')
    cpbar = ProgressBar(maxval=100).start()
    colours = []
    for filename_abs in extracted_files:
        img = Image.open(filename_abs)
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

    output_path = f'{sys.argv[2]}/{file_basename}.png' if len(sys.argv) > 2 else f'{file_path}.png'

    print(f'[INFO] Done! Work time: {str(datetime.timedelta(seconds=work_time))}')
    return out_img, output_path


def main():
    # CHECKING INPUT ARGUMENT
    if len(sys.argv) < 2:
        print(f'{OutColours.ERROR}[ERROR] Missing argument: input file{OutColours.END}')
        exit(1)

    # DEFINING INPUT
    input_path = sys.argv[1]

    # EMPTYING TEMP DIRECTORY
    if os.path.isdir(WORK_DIR):
        rmtree(WORK_DIR)
    os.makedirs(WORK_DIR)

    # CHECKING INPUT EXISTENCE
    dir_as_input = False
    if os.path.isdir(input_path):
        dir_as_input = True
        print(f'[INFO] Input directory: {os.path.abspath(input_path)}')
    elif os.path.isfile(input_path):
        print(f'[INFO] Input file: {os.path.abspath(input_path)}')
    else:
        print(f'{OutColours.ERROR}[ERROR] Input path is invalid{OutColours.END}')
        raise Exception('Input path is invalid')

    # RUNNING EXTRACTION PROCESS
    if dir_as_input:
        video_files = read_files(input_path)
        print(video_files)
        with Pool() as pool:
            results = pool.map(process_video_file, video_files)
            for img, path in results:
                img.save(path)
                print(f'[INFO] Saved image to {path}')
    else:
        img, path = process_video_file(input_path)
        img.save(path)
        print(f'[INFO] Image saved to {path}')

    # REMOVING TEMP DIRECTORY
    rmtree(WORK_DIR, ignore_errors=True)


if __name__ == '__main__':
    if sys.platform == 'darwin':
        set_start_method('fork')
    print(f'[DEBUG] MultiProcessing start method is {get_start_method()}')

    try:
        main()
    except Exception as e:
        print(f'{OutColours.ERROR}[ERROR] Error: {e}{OutColours.END}')
