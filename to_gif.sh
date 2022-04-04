#!/bin/bash
if [ $# -ne 4 ]; then
    echo "./to_git.sh [movie_file_name] [start(sec)] [length(sec)] [gif_width]"
    exit
fi
ffmpeg -ss $2 -t $3 -i $1 -vf scale=$4:-1,fps=20 $1.scaled.mp4
ffmpeg -i $1.scaled.mp4 -vf palettegen $1.png
ffmpeg -i $1.scaled.mp4 -i $1.png -filter_complex paletteuse $1.gif -y
rm -f $1.png $1.scaled.mp4
