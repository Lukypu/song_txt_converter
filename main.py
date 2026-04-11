# -*- coding: utf-8 -*-
"""
Created on 2026-04-11

@author: Lukypu

Description: 
    main function for parser and formatter script

Todo: 
    DONE 1) create git version control and divide into seperate files -- main file, song&parser file, formatter file
    2) add .tex parser and one page latex pdf printout
    DONE 3) move verse_count to Formatters       
    4) add argparse utility
    5) add minimize utility
    6) improve bridge and chorus recognition <=> based on shared/unshared chords
    DONE 7) Improve verse count utility
    8) add manual add of metadata in song -- title and author
    9) add __call__ for lines
"""
from parser import Parser
from formatter import ChordProFormatter


if __name__ == "__main__":

    path = "/home/lukypu/Personal/Kytara/Songbook/ultimate-guitar/"
    
    with open(f"{path}/johnny_cash-ghost_riders_in_the_sky-ultsg.txt", "r") as f:

        text = f.read()

        parser = Parser(text)
        parser.song_parser()
        parser.minimize("verse")
        song = parser()

    output = song.render(ChordProFormatter(), verse_count=0)

    with open(f"{path}/johnny_cash-ghost_riders_in_the_sky-ultsg-test.chord", "w") as f:
        f.write(output)
