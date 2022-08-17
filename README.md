# Film Colours Over Time

**The stupid name hides a useless idea.**\
This Python script convert a given video file into a picture, by taking a frame every *n* seconds, calculating the average colour of that frame, and adding a vertical line to the output picture with the given colour.
> The script uses [FFMpeg](https://www.ffmpeg.org/) to extract the frames, so it is required for it to work.

## Usage

### Single-file mode
**`python3 <input file path> <optional: output file path>`**<br/>
When wanting to process a single video file, the first argument needs to be the input video file, and the second optional argument can be the output image file.<br/>
Example:<br/>
 - `python3 ~/Movies/MyVideo.mp4`: output file will be *~/Movies/MyVideo.mp4.png*
 - `python3 ~/Movies/MyVideo.mp4 ~/Photos/Output.png`: output file will be *~/Photos/Output.png*

### Directory mode
**`python3 <input directory path> <optional: output directory path>`**<br/>
For processing multiple video files within the same directory, simply input the path of the directory.<br/>
Example:<br/>
 - `python3 ~/Movies/SomeVideos/`: will process all video files within the folder and output the pictures in the same manner as the single-file mode
 - `python3 ~/Movies/SomeVideos/ ~/Photos/FCOT-Images/`: the images will be inside of the *~/Photos/FCOT-Images/* directory, following the same naming used in the single-file mode (~/Movies/SomeVideos/MyVideo.mp4 will generate ~/Photos/FCOT-Images/MyVideo.mp4.png)
