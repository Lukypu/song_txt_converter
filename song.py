# -*- coding: utf-8 -*-
"""
Created on 2026-04-11

@author: Lukypu

Description: 
    Song classes for formatter script

Todo: 
"""


class SongLine:
    def __init__(self, line_string, type):
        allowed_types = ["chords", "empty", "lyrics", "comment"]

        if any([type == allowed for allowed in allowed_types]):
            self.type = type
        else:
            self.type = None
        
        self.content = line_string



class SongPart:
    def __init__(self, type):
        # Idea: cut song into parts: Header, Intro, Verse(s), Chorus(es), Bridge(s), Instrumental, Break, Outro
        allowed_types = ["intro", "verse", "chorus", "bridge", "instrumental", "outro", "chords"]

        if any([type == allowed for allowed in allowed_types]):
            self.type = type
        else:
            self.type = None

        self.lines = []

    def add(self, line):
        self.lines.append(line)

    def delete_line(self, idx, type = None):

        if type is None:
            del self.lines[idx]

        else:
            count = 0
            for i, line in enumerate(self.lines):

                if line.type == "lyrics":
                    count +=1
                
                if count == idx+1:
                    if type == "lyrics":
                        del self.lines[i]
                    
                    # deletes chords over idx-th line
                    elif type == "chords" and (i-1>=0):
                        if self.lines[i-1].type == "chords":
                            del self.lines[i-1]
                        
        

class Song:
    def __init__(self, meta_data, song_parts, source = None, language=None, header_string = None, footer_string = None):

        self.header = meta_data.get("string", "") + (header_string or "")
        if 'string' in meta_data: 
            del meta_data["string"]

        if meta_data.get("source") is None:
            meta_data["source"] = source

        if meta_data.get("language") is None:
            meta_data["language"] = language

        self.metadata = meta_data
        
        for part in song_parts:
            if part.type == "chords":
                part.type = "instrumental"
        self.song_parts = song_parts
        self.footer = footer_string


    def add(self, part):
        self.song_parts.append(part)



    def render(self, formatter, verse_count=None):
        output = []

        # --- metadata ---
        output.extend(formatter.metadata(self.metadata))

        # --- header ---
        if self.header:
            output.extend(formatter.header(self.header))

        # --- parts ---
        output.extend(formatter.format_parts(self.song_parts))

        # --- footer ---
        if self.footer:
            output.append(formatter.footer(self.footer))

        return "\n".join(output)
    
if __name__ == "__main__":
    pass