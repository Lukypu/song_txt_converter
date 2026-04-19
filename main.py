#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2026-04-11

@author: Lukypu

Description: 
    main function for parser and formatter script

Done:
    DONE - create git version control and divide into seperate files -- main file, song&parser file, formatter file
    DONE - add .tex parser and one page latex pdf printout
    DONE - move verse_count to Formatters       
    DONE - Improve verse count utility
    DONE - add argparse utility
    DONE - add manual add of metadata in song -- title and author
    DONE - Parse pisnicky-akordy.cz better
Todo: 
    - improve minimize utility
    - add maximaze utility
    - european <--> american chord convention converter
    - Docstrings and list of options (that is going to be part of CLI)
    - improve reading of chords divided by "|"
    - Latex: rewrite instrumentals as bridge ---> Bude lepší použít leadsheets

Todo ideas:
    - add __call__ for lines
"""
from parser import Parser
from formatter import ChordProFormatter, TexFormatter, TxtFormatter
import argparse
import os
from datetime import datetime

if __name__ == "__main__":

#     # So called naive way
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
    cmd_parser.add_argument('-o', '--output', type=str, help="Path to output file")
    
    cmd_parser.add_argument('-m', '--minimize', action="store_true", help="Compresses repeated chords occurances")
    cmd_parser.add_argument('-x', '--maximize', action="store_true", help="Inflates song by adding choruses and verses explicitely, if they are identical to some preceding")
    cmd_parser.add_argument('-v', '--verse_count', action="store_true", help="Wheather format with the verse numbering explicitely written")
    cmd_parser.add_argument('-l', '--language', type=str, help="Language in which the song is written")
    cmd_parser.add_argument('--footer', type=str, help="String to be printed at the end of a song")
    cmd_parser.add_argument('--header', type=str, help="String to be printed before the beginning of the song")
    cmd_parser.add_argument('--source', type=str, help="String to be remarked as the source metadata of the song")
    cmd_parser.add_argument('--csv', type=str, help="Path to csv. Appends information about current song being processed to the csv")
    # cmd_parser.add_argument('--date', action="store_true", help="Append current date as 'creation_date: YYYY-MM-DD'")

    cmd_parser.add_argument('-t', '--title', type=str, help="Name of the song")
    cmd_parser.add_argument('-a', '--artist', type=str, help="Author of the song")
    cmd_parser.add_argument('-c', '--chords_conversion', action="store_true", help="Convert chords to european notation (B->H, Bb->B)")

    args = cmd_parser.parse_args()

    # reading source file
    with open(args.input, "r") as f:
        text = f.read()

    # parsing text
    parser = Parser(text)
    parser.song_parser()
    if args.minimize:
        parser.minimize()
    
    if args.maximize:
        parser.maximize()

    song = parser()


    # here I need to pass title, name, source, language, header and footer
    if args.header:
        song.header = song.header + args.header
        # Dunno, maybe song.header = "\n".join([song.header, args.header])
        # It is to be seen if it is used
    
    if args.footer:
        song.footer = song.footer + args.footer

    fields = ["title", "artist" "source", "language"]

    for field in fields:
        value = getattr(args, field, None)
        if value:
            song.metadata[field] = value
        

    # choosing formatter and formating
    if args.output.endswith("tex"):
        formatter = TexFormatter()
    
    elif args.output.endswith("txt"):
        formatter = TxtFormatter()

    elif args.output.endswith("crd") or args.output.endswith("chord") or args.output.endswith("chordpro"):
        formatter = ChordProFormatter()
    
    else:
        raise ValueError("Unknown extension")

    if args.verse_count:
        args.verse_count = True
    else:
        args.verse_count = False

    if args.chords_conversion:
        args.chords_conversion = True
    else:
        args.chords_conversion = False


    output = song.render(formatter, verse_count = args.verse_count, chords_conversion = args.chords_conversion)

    
    # writing in output
    # writes into output path if given else just on the screen
    if args.output:

        base = os.path.splitext(args.input)[0]
        ext = args.output.lstrip(".").lower()
 
         # check if output_arg already has an extension
        if os.path.splitext(args.output)[1]:
            pass  # already full filename keep as it is

        else:
            # otherwise treat as extension
            args.output = f"{base}.{ext}"

        with open(args.output, "w") as output_file:
            output_file.write(output)

    else:
        print(output)


    # write line into csv
    if args.csv:
        with open(args.csv, "a") as csv:
            # format title, artist, filename, date_added, language, source, 
            csv.write(f"{song.metadata['title']};{song.metadata['artist']};{args.output};{datetime.now().strftime('%Y-%m-%d')};{args.language};{args.source}\n")

    