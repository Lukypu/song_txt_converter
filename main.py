# -*- coding: utf-8 -*-
"""
Created on 2026-04-11

@author: Lukypu

Description: 
    main function for parser and formatter script

Todo: 
"""
from parser import song_parser
from formatter import ChordProFormatter


if __name__ == "__main__":

    path = "/home/lukypu/Personal/Kytara/Songbook/ultimate-guitar/"
    
    with open(f"{path}/johnny_cash-ghost_riders_in_the_sky-ultsg.txt", "r") as f:

        song = song_parser(f)

    output = song.render(ChordProFormatter(), verse_count=0)

    with open(f"{path}/johnny_cash-ghost_riders_in_the_sky-ultsg.chord", "w") as f:
        f.write(output)
