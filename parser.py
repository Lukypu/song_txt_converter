# -*- coding: utf-8 -*-
"""
Created on 2026-04-11

@author: Lukypu

Description: 
    Parser part for song parser script

Todo: 
"""
import re

from utils import chord_pattern, is_chord
from song import Song, SongLine, SongPart

def get_line_type(line):

    def detect_section(line):
        """
        Detect section type from a line like:
        [Verse 1], Chorus:, --- bridge ---, etc.
        Returns normalized section name or None.
        """

        SECTION_PATTERNS = {
            "intro": r"\bintro\b",
            "verse": r"\bverse(s)?\b",
            "chorus": r"\bchorus(es)?\b",
            "bridge": r"\bbridge(s)?\b",
            "instrumental": r"(\binstrumental\b|\bsolo\b|\bbreak\b)",
            "outro": r"\boutro\b",
        }

        if not line:
            return None

        # Remove common wrappers/symbols
        line = re.sub(r'[\[\]\(\)\{\}:_\-]', ' ', line.lower())
        line = re.sub(r'\s+', ' ', line.lower()).strip()

        # Search for section keywords
        for name, pattern in SECTION_PATTERNS.items():
            if re.search(pattern, line):
                return name

        return None

    if line.strip() == "":
        return "EMPTY"

    tokens = line.split()

    if all([is_chord(token) for token in tokens]):
        return "CHORDS"

    # checking length eliminates matching lyrics "verse" while allowing 
    # some flexibility with punctuation etc.
    if detect_section(line) is not None:
        return f"{detect_section(line).upper()}_MARKER"

    if re.match(r"^[0-9].*", line):
        return "VERSE_BEGIN"
    
    if re.match(r"^R\w{0,2}:.*", line):
        return "CHORUS_BEGIN"
    
    if re.match(r"^\*\s*\)?\s*:", line):
        return "BRIDGE_BEGIN"

    return "SIMPLE"


class Parser:

    def __init__(self, text):

        self.text_lines = text.split("\n")
        self.idx_start_of_chords = 0
        self.metadata = None
        self.song_parts = None
        self.song = None

    def __call__(self, minimize = False):

        if self.song is None:
            self.song_parser()

        return self.song

    def header_parser(self, meta_data_pattern = r'^([A-Za-z_]+):\s*(.*)$'):

        meta_data = {
            # common/chordpro metadate
            "title": "title",
            "artist": "artist",
            "album": None,
            "key": None,
            "capo": None,
            "tempo": None,
            "time": None,
            "year": None,
            "composer": None,
            # my own metadata
            "language" : None,
            "source" : None,
            "string" : [],
            "date" : None,
        }

        meta_pattern = re.compile(rf'{meta_data_pattern}')

        # read and parse header
        idx_start_of_chords = 0
        for idx, line in enumerate(self.text_lines):
            line_type = get_line_type(line)

            if line_type == "CHORDS" or line_type.endswith("_MARKER"):
                idx_start_of_chords = idx
                break
            
            if idx == 0 and line_type != "EMPTY":
                meta_data["title"] = line.strip()

            elif idx == 1 and line_type != "EMPTY":
                meta_data["artist"] = line.strip()

            else:
                m = meta_pattern.match(line)
                if m:
                    key = m.group(1).strip().lower()
                    value = m.group(2).strip()
            
                    if key in meta_data:
                        meta_data[key] = value
                    else:
                        # unknown metadata comment out
                        meta_data["string"].append(value)
                else:
                    if line_type == "EMPTY":
                        continue
                    else:
                        meta_data["string"].append(line)

        # formate the string in the metadata to single string
        if meta_data["string"] is not []:
            meta_data["string"] = "\n".join(meta_data["string"])

        self.metadata = meta_data
        self.idx_start_of_chords = idx_start_of_chords

 
    def body_parser(self):

        def clean_section_markers(song_part):
            """
            Removes inline section markers and adjusts chord alignment above.
            Works in-place on SongPart.
            """

            MARKER_REGEX = re.compile(
                r'^\s*(?:'
                r'R:|Ref:|'          # chorus markers
                r'\d+\s*[:\.)]?|'      # 1:, 1., 1 , 1
                r'\s*'
                r')\s*'
            )

            lines = song_part.lines
            marker_len = 0

            for i in range(len(lines)):

                if lines[i].type == "chords":
                    continue

                line = lines[i].content

                match = MARKER_REGEX.match(line)
                if not match:
                    continue

                marker_len = match.end()

                # remove marker from lyric line
                lines[i].content = line[marker_len:]


                # adjust preceding chord line if present
                if i > 0 and lines[i - 1].type == "chords":
                    prev = lines[i - 1].content

                    # remove same number of characters from chord line
                    # but never go below 0
                    cut = min(len(prev), marker_len)
                    lines[i - 1].content = prev[cut:]

            song_part.lines = lines

            return song_part

        # where to store parsed song parts
        song_parts = []
        current_songpart = None
        inline_markers = False

        for idx, line in enumerate(self.text_lines[self.idx_start_of_chords:]):
            linetype = get_line_type(line)

            # skip empty lines
            if linetype == "EMPTY":

                # classifiyng different instances of plain chords parts
                if current_songpart is not None and current_songpart.type == "chords":

                    if song_parts == []:
                        current_songpart.type = "intro"

                    elif idx == len(self.text_lines):
                        current_songpart.type = "outro"

                    else:
                        current_songpart.type= "instrumental"

                # wrap up the current song part
                elif current_songpart is not None and current_songpart.lines !=  []:

                    if inline_markers:
                        current_songpart = clean_section_markers(current_songpart)

                    song_parts.append(current_songpart)
                    current_songpart = None

                # should cover other instances, mainly if songpart not none and type is not "chords"
                else:
                    continue

            # UG-style "full-line" markers
            elif linetype.endswith("_MARKER"):
                current_songpart = SongPart(linetype.split("_")[0].lower())
                continue
            
            # line with chords
            elif linetype == "CHORDS":

                if current_songpart is None:
                    if idx == len(self.text_lines):
                        current_songpart = SongPart("outro")
                    else:
                        current_songpart = SongPart("chords")

                current_songpart.add(SongLine(line, "chords"))
                
                continue

            # Lines umarked beforehand which might have been preceded with a line of chords
            # => classify into verse, chorus and bridge
            elif current_songpart is None or current_songpart.type == "chords":

                if current_songpart is None:
                    current_songpart == SongPart(None)

                if linetype.endswith("_BEGIN"):
                    inline_markers = True

                # "inline"/no markers
                if linetype == "VERSE_BEGIN":
                    current_songpart.type = "verse"

                elif linetype == "CHORUS_BEGIN":
                    current_songpart.type = "chorus"

                elif linetype == "BRIDGE_BEGIN" or linetype == "SIMPLE":
                    current_songpart.type = "bridge"

                current_songpart.add(SongLine(line, "lyrics"))

            elif linetype == "SIMPLE" and current_songpart.type in ["verse", "chorus", "bridge"]:
                current_songpart.add(SongLine(line, "lyrics"))

            else:
                print(current_songpart.type)
                print(linetype)
                print(line)
                raise ValueError("Unexpected Behaviour")


        if current_songpart is not None:

            if current_songpart.type == "chords":
                current_songpart.type = "outro"

            if inline_markers:
                current_songpart = clean_section_markers(current_songpart)

   
            song_parts.append(current_songpart)

        
        self.song_parts = song_parts

    def song_parser(self):

        self.header_parser()
        self.body_parser()
        
        self.song = Song(self.metadata, self.song_parts)


    def minimize(self, lyrics = False):
        
        def get_chord_progression(song_part):

            chords_list = []
            for song_line in song_part.lines:
                if song_line.type == "chords":
                    chords = song_line.content.strip().split()
                    chords_list.append(chords)
            
            return chords_list



        def get_lyrics(song_part):
            
            words_list = []
            for song_line in song_part.lines:
                if song_line.type == "lyrics":
                    words = song_line.content.strip().split()
                    words_list.append(words)

            return words_list
            

        def minimize_target(target):
            # go through song parts and compare lyrics and chords --> remove what need not be
            object_chords = []
            object_lyrics = []
            for i, song_part in enumerate(self.song_parts):

                # initialize chords and lyrics to compare to
                if song_part.type == target and len(object_chords) == 0:
                    object_chords = get_chord_progression(song_part)
                    object_lyrics = get_lyrics(song_part)

                elif song_part.type == target and len(object_chords) != 0:

                    # compare the chords of first instance with current one --> delete if same
                    current_chords = get_chord_progression(song_part)
                    row_count = min(len(object_chords), len(current_chords))

                    for idx in range(row_count):
                        if current_chords[idx] == object_chords[idx]:

                            song_part.delete_line(idx, "chords")


                    # compare lyrics with the first instance --> if all same and all chords deleted --> delete
                    # TODO

                self.song_parts[i] = song_part

        for target in ["verse", "chorus"]:
            minimize_target(target)

    def maximize():
        pass


        



                    

                
