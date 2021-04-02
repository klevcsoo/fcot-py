# Film Colours Over Time

**The stupid name hides a useless idea.**\
This Python script convert a given video file into a picture, by taking every *x* frame, calculating the average colour of that frame, and adding a vertical line to the output picture with the given colour.

## Usage
The first argument need to be th input video file, and the second argument can be the output image file.\
**`python3 main.py <input video file> <optional: output image file>`**

If the output file is left out, it will be put into the same directory, that the input file is located in.\
For example, `python3 main.py ~/Videos/film.mp4` will result in the output file having the path of *~/Videos/film.mp4.png*.

### This does require FFMpeg to be installed on your system.
