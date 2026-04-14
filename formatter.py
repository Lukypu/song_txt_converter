# -*- coding: utf-8 -*-
"""
Created on 2026-04-11

@author: Lukypu

Description: 
    Formatter part for song parser script

Todo: 
"""
import re

from utils import chord_pattern, is_chord
from song import Song, SongLine, SongPart

class Formatter():

    STANDARD_META = {
        "title",
        "artist",
    }

    MY_META = {
        "language",
        "date",
        "source",
    }

    # format individual lines and objects
    def format_chord(self, chord):
        pass

    def meta_line_print(self, key, value):
        pass

    def comment_out_line(self, string):
        pass

    def print_out_line(self, string):
        pass

    def start_of_type(self, type, label = None):
        pass

    def end_of_type(self, type):
        pass

    def format_chords_over_lyrics_line(self, chords, lyrics):
        pass

    def format_lyrics_line(self, line):
        # often just repeat the line unless stated otherwise
        return line

    def format_chords_line(self, line):
        chord_occurances = self.find_overline_chords(line)
        out_str = []

        for chord_occurence in chord_occurances:
            pos, chord = chord_occurence
            chord = self.format_chord(chord)
            out_str.append(chord + " ")

        out_str = "".join(out_str)

        return out_str


    def format_chords_over_lyrics_line(self, chord_line, lyrics_line):
        return [self.match_chord_lyrics(chord_line, lyrics_line)]


 
    # format parts of song: metadata, header, part, parts, footer
    def metadata(self, meta):
        out = []

        for key, value in meta.items():
            if value is None:
                continue

            key_norm = key.lower().strip()
            value = str(value).strip()

            if not value:
                continue

            # --- standard chordpro metadata ---
            if key_norm in self.STANDARD_META:
                out.append(self.meta_line_print(key, value))

            # --- non-standard to be noted (no print) ---
            elif key_norm in self.MY_META:
                out.append(self.comment_out_line(f"{key}: {value}"))

            # --- non-standard to be printed ---
            else:
                out.append(self.print_out_line(f"{key}: {value}"))
        

        return out

    def header(self, header_string):
        if len(header_string) == 0:
            return []

        out = []

        # Split into lines safely
        lines = header_string.splitlines()

        for line in lines:
            line = line.strip()

            if not line:
                out.append("")  # preserve blank line
                continue

            out.append(self.print_out_line(line))

        out.append("")
        return out



    def format_part(self, part, verse_count = None):
        out = []

        if part.type in ["verse", "chorus", "bridge"]:
            if self.start_of_type is not None:
                if part.type == "verse" and verse_count is not None:
                    out.append(self.start_of_type(part.type, label = verse_count))
                else:  
                    out.append(self.start_of_type(part.type))

            chord_container = None
            for line in part.lines:

                if line.type == "chords":
                    chord_container = line.content.rstrip()

                elif line.type == "lyrics" and chord_container is not None:

                    print_out_lines = self.format_chords_over_lyrics_line(chord_container, line.content)
                    for print_out_line in print_out_lines:
                        out.append(print_out_line)

                    chord_container = None

                elif line.type == "lyrics" and chord_container is None:
                    out.append(self.format_lyrics_line(line.content.rstrip()))

                else:
                    raise ValueError

            if self.end_of_type(part.type) is not None:
                out.append(self.end_of_type(part.type))

            out.append("") # empty line at the end

        
        if part.type in ["intro", "instrumental", "outro", "chords"]:
            for line in part.lines:
                out.append(self.format_chords_line(line.content.rstrip()))
            
            out.append("")

        return out
 


    def format_parts(self, parts, verse_count = None):

        output = []

        if verse_count is not None:
            verse_count = 0

        for part in parts:
            if verse_count is not None and part.type == "verse":
                verse_count +=1

            output.extend(self.format_part(part, verse_count))
        
        return output


    def footer(self, footer_string):
        pass



    # Formating extras/utilities
    def find_overline_chords(self, chord_line):

        chord_regex = re.compile(chord_pattern())
        chord_occurances = []

        for m in chord_regex.finditer(chord_line):
            chord = m.group()
            if chord[-1] in [",", " "]:
                chord = chord[:-1]

            pos = m.start()
            chord_occurances.append((pos, chord))

        return chord_occurances
    
    def match_chord_lyrics(self, chord_line, lyrics_line):
        # save chords along with their position for later reconstruction
        chord_occurances = self.find_overline_chords(chord_line)

        next_chord_iter = iter(chord_occurances)
        next_chord = next(next_chord_iter)
        out_str = []
        extra_chords = True

        for i, char in enumerate(lyrics_line):
            pos, chord = next_chord

            # matching the chords with the respective lyrics
            if i == pos:
                out_str.append(self.format_chord(chord))
                try:
                    next_chord = next(next_chord_iter)
                except StopIteration:
                    # no more chords
                    extra_chords = False

            out_str.append(char)

        # chords located after the end of the line with lyrics
        while extra_chords:
            try:
                pos, chord = next_chord
                out_str.append(self.format_chord(chord))
                next_chord = next(next_chord_iter)
            except StopIteration:
                extra_chords = False

        out_str = "".join(out_str)

        return out_str



class TexFormatter(Formatter):

    def format_chord(self, chord):

        chord = re.sub(r'(?<=[A-H])b', '&', chord)

        return f"\\[{chord}]"
 
    # format individual lines and objects
    def meta_line_print(self, key, value):
        return f"% {key}: {value}"

    def comment_out_line(self, string):
        return f"% {string}"

    def print_out_line(self, string):
        return f"\\textnote{{{string}}}"

    def start_of_type(self, type, label = None):
        if type == "bridge":
            return f"\\beginverse*"
        else:
            return f"\\begin{type}"

    def end_of_type(self, type):
        if type == "bridge":
            return f"\\endverse"
        else:
            return f"\\end{type}"


    def format_lyrics_line(self, line):
        # often just repeat the line unless stated otherwise
        return line

    def format_chords_line(self, line):
        return f"{{\\nolyrics {super().format_chords_line(line)}}}"

    def format_chords_over_lyrics_line(self, chord_line, lyrics_line):
        return [self.match_chord_lyrics(chord_line, lyrics_line)]

   
    # formatting of individual parts
    def metadata(self, meta_data):

        out = []
        out.append("\\beginsong{" + meta_data["title"].strip() + "}[by={\\normalsize " + meta_data["artist"].strip() + "}]")
        out.extend(super().metadata(meta_data))

        return out
    
    def header(self, header_string):
        return super().header(header_string)
    
    def format_part(self, part, verse_count=None):
        return super().format_part(part, verse_count)
    
    def format_parts(self, parts):
        return super().format_parts(parts)

    def footer(self, footer_string):
        if footer_string is not None:
            return [self.print_out_line(footer_string), f"\\endsong"]
        else:
            return [f"\\endsong"]

    
    # utilities
    def find_overline_chords(self, chord_line):
        return super().find_overline_chords(chord_line)
    
    def match_chord_lyrics(self, chord_line, lyrics_line):
        return super().match_chord_lyrics(chord_line, lyrics_line)


class ChordProFormatter(Formatter):
    
    def format_chord(self, chord):
        return f"[{chord}]"

        
    STANDARD_META = {
        "title",
        "artist",
        "album",
        "composer",
        "lyricist",
        "key",
        "time",
        "tempo",
        "capo",
        "year",
        "duration",
    }

    def meta_line_print(self, key, value):
        return (f"{{{key}: {value}}}")

    def comment_out_line(self, string):
        return f"# {string}" 

    def print_out_line(self, string):
        return f"{{comment: {string}}}"

    def start_of_type(self, type, label = None):
        if label is not None:
            return f"{{start_of_{type}: label='{label}'}}"
        else:  
            return f"{{start_of_{type}}}"

    def end_of_type(self, type):
        return f"{{end_of_{type}}}"

    def format_lyrics_line(self, line):
        # often just repeat the line unless stated otherwise
        return line

    def format_chords_line(self, line):
        return super().format_chords_line(line)

    def format_chords_over_lyrics_line(self, chord_line, lyrics_line):
        return [self.match_chord_lyrics(chord_line, lyrics_line)]


   
    # formatting of individual parts
    def metadata(self, meta_data):
        return super().metadata(meta_data)
    
    def header(self, header_string):
        return super().header(header_string)
    
    def format_part(self, part, verse_count=0):
        return super().format_part(part, verse_count=verse_count)
    
    def format_parts(self, parts):
        return super().format_parts(parts)

    def footer(self, footer):
        if footer is None:
            return None
        else:
            return [self.print_out_line(footer.strip())]

    # utilities
    def find_overline_chords(self, chord_line):
        return super().find_overline_chords(chord_line)
    
    def match_chord_lyrics(self, chord_line, lyrics_line):
        return super().match_chord_lyrics(chord_line, lyrics_line)
    

class TxtFormatter(Formatter):

    def format_chord(self, chord):
        return chord

    def meta_line_print(self, key, value):
        return (f"{key}: {value}")

    def comment_out_line(self, string):
        return f"# {string}" 

    def print_out_line(self, string):
        return f"{string}"

    def start_of_type(self, type, label = None):
        if label is not None:
            return f"[{type} {label}]"
        else:  
            return f"[{type}]"

    def end_of_type(self, type):
        return None

    def format_lyrics_line(self, line):
        # often just repeat the line unless stated otherwise
        return line

    def format_chords_line(self, line):
        return super().format_chords_line(line)

    def format_chords_over_lyrics_line(self, chord_line, lyrics_line):
        return [chord_line, lyrics_line]


   
    # formatting of individual parts
    # This could be done better by just redefining my and accepted metadata
    def metadata(self, meta):
        out = []

        for key, value in meta.items():
            if value is None:
                continue

            key_norm = key.lower().strip()
            value = str(value).strip()


            if key_norm in self.STANDARD_META and (key_norm == "title" or key_norm == "artist"):
                out.append(value)

            # --- standard chordpro metadata ---
            elif key_norm in self.STANDARD_META:
                out.append(self.meta_line_print(key, value))

            # --- non-standard to be noted (no print) ---
            elif key_norm in self.MY_META:
                out.append(self.print_out_line(f"{key}: {value}"))

            # --- non-standard to be printed ---
            else:
                out.append(self.print_out_line(f"{key}: {value}"))
        

        return out

   
    def header(self, header_string):
        return super().header(header_string)
    
    def format_part(self, part, verse_count=0):
        return super().format_part(part, verse_count=verse_count)
    
    def format_parts(self, parts):
        return super().format_parts(parts)

    def footer(self, footer):
        if footer is None:
            return None
        else:
            return [self.print_out_line(footer.strip())]

    # utilities
    def find_overline_chords(self, chord_line):
        return super().find_overline_chords(chord_line)
    
    def match_chord_lyrics(self, chord_line, lyrics_line):
        return super().match_chord_lyrics(chord_line, lyrics_line)
 


if __name__ == "__main__":
    pass