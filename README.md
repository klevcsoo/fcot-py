# Film Colours Over Time

**The stupid name hides a useless idea.**\
This Python script convert a given video file into a picture, by taking a frame every *n* seconds, calculating the average colour of that frame, and adding a vertical line to the output picture with the given colour.
> The script uses [FFMpeg](https://www.ffmpeg.org/) to extract the frames, so it is required for it to work.

## Usage
The first argument needs to be th input video file, and the second argument can be the output image file.\
**`python3 main.py <input video file> <optional: output image file>`**

If the output file is left out, it will be put into the same directory, that the input file is located in.\
For example, `python3 main.py ~/Videos/film.mp4` will result in the output file having the path of *~/Videos/film.mp4.png*.

### No pull requests are accepted for this repository.
