# -*- coding: utf-8 -*-
"""
Created on 2026-04-11

@author: Lukypu

Description: 
    main function for parser and formatter script

Done:
    DONE 1) create git version control and divide into seperate files -- main file, song&parser file, formatter file
    DONE 2) add .tex parser and one page latex pdf printout
    DONE 3) move verse_count to Formatters       
    DONE 7) Improve verse count utility
Todo: 
    4) add argparse utility
    8) add manual add of metadata in song -- title and author
        --> ie. CLI support 
    [partial] 5) add minimize utility
    9) european <--> american chord convention converter
    10) Docstrings and list of options (that is going to be part of CLI)
    11) Parse pisnicky-akordy.cz better

Todo ideas:
    - improve bridge and chorus recognition <=> based on shared/unshared chords
    - add __call__ for lines
"""
from parser import Parser
from formatter import ChordProFormatter, TexFormatter, TxtFormatter
import argparse

if __name__ == "__main__":

#     path = "/home/lukypu/Personal/Kytara/Songbook/ultimate-guitar/"
#     
#     with open(f"{path}/johnny_cash-ghost_riders_in_the_sky-ultsg.txt", "r") as f:
# 
#         text = f.read()
# 
#         parser = Parser(text)
#         parser.song_parser()
#         parser.minimize("verse")
#         song = parser()
# 
#     output = song.render(TxtFormatter(), verse_count=0)
#     # output = song.render(ChordProFormatter(), verse_count=0)
# 
#     with open(f"{path}/johnny_cash-ghost_riders_in_the_sky-ultsg-test.txt", "w") as f:
#         f.write(output)
# 
    cmd_parser = argparse.ArgumentParser()

    cmd_parser.add_argument('input', type=str, help="Input file with chords and lyrics")
    cmd_parser.add_argument('-o', '--output', type=str, required=True, help="Path to output file")
    
    cmd_parser.add_argument('-m', '--minimize', type=bool, help="Compresses repeated chords occurances")
    cmd_parser.add_argument('-x', '--maximize', type=str, help="Inflates song by adding choruses and verses explicitely, if they are identical to some preceding")
    cmd_parser.add_argument('-v', '--verse_count', action="True", help="Wheather format with the verse numbering explicitely written")
    cmd_parser.add_argument('-l', '--language', type=str, help="Language in which the song is written")
    cmd_parser.add_argument('--footer', type=str, help="String to be printed at the end of a song")
    cmd_parser.add_argument('--header', type=str, help="String to be printed before the beginnig of the song")
    cmd_parser.add_argument('--source', type=str, help="String to be remarked as the source metadata of the song")
    cmd_parser.add_argument('--csv', type=str, help="Path to csv. Appends information about current song being processed to the csv")
    # cmd_parser.add_argument('--date', type=bool, help="Append current date as 'creation_date: YYYY-MM-DD'")

    cmd_parser.add_argument('-n', '--name', type=str, help="Name of the song")
    cmd_parser.add_argument('-a', '--author', type=str, help="Author of the song")
    cmd_parser.add_argument('-e', '--to_european', action="store_true", help="Convert chords to european notation (B->H, Bb->B)")

