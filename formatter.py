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
    def metadata(self, meta_data):
        pass
    def header(self, header_string):
        pass
    def format_part(self, part):
        pass
    def format_parts(self, parts):
        pass
    def footer(self, footer_string):
        pass
    def format_chord(self, chord):
        pass

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
    pass



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

    MY_META = {
        "language",
    }

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
                out.append(f"{{{key_norm}: {value}}}")

            # --- non-standard to be noted (no print) ---
            elif key_norm in self.MY_META:
                out.append(f"# {key_norm}: {value}")

            # --- non-standard to be printed ---
            else:
                out.append(f"{{comment: {key_norm}: {value}}}")
        

        return out

    def header(self, header_string):
        if not header_string:
            return []

        out = []

        # Split into lines safely
        lines = header_string.splitlines()

        for line in lines:
            line = line.strip()

            if not line:
                out.append("")  # preserve blank line
                continue

            out.append(f"{{comment: {line}}}")

        out.append("")
        return out


    def format_part(self, part, verse_count = None):
        out = []

        if part.type in ["verse", "chorus", "bridge"]:
            if part.type == "verse" and verse_count is not None:
                out.append(f"{{start_of_{part.type}: label='{verse_count}:'}}")
            else:  
                out.append(f"{{start_of_{part.type}}}")

            chord_container = None
            for line in part.lines:

                if line.type == "chords":
                    chord_container = line.content.strip()

                elif line.type == "lyrics" and chord_container is not None:
                    chords_inline = self.match_chord_lyrics(chord_container, line.content)
                    out.append(chords_inline.strip())
                    chord_container = None

                elif line.type == "lyrics" and chord_container is None:
                    out.append(line.content.strip())

                else:
                    raise ValueError

            out.append(f"{{end_of_{part.type}}}")
            out.append("")

        
        if part.type in ["intro", "instrumental", "outro", "chords"]:
            for line in part.lines:
                out.append(f"[{line.content.strip()}]")
            
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

    def footer(self, footer):
        return [f"{{comment: {footer.strip()}}}"]


if __name__ == "__main__":
    pass