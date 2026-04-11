# Song Formatter

A lightweight Python tool for parsing chord/lyrics text (e.g. from Ultimate Guitar) and exporting it into structured formats such as **ChordPro** and **LaTeX**.

This was inspired by and built upon a fantastic script by kasnerz, more about him here: 
[https://github.com/kasnerz/chords2latex]

The code also uses parts of his code.

---

## Features

* Parses raw song text into structured components:

  * metadata
  * sections (verse, chorus, bridge, etc.)
  * chord and lyric lines
* Converts songs into:

  * ChordPro format
  * LaTeX format (extensible)
* Preserves chord alignment using column-based positioning
* Handles common real-world variations in song formatting

---

## Project Structure

```
.
├── main.py        # Entry point
├── parser.py      # Parses raw text → Song object
├── model.py       # Song, SongPart, SongLine classes
├── formatter.py   # Output formatters (ChordPro, TeX)
└── utils.py       # Shared helpers (e.g. line type detection)
```
---

## Extending

To add a new format:

1. Create a new formatter class in `formatter.py`
2. Implement a `render(song)` method
3. Use it in `main.py`

---

## Notes

* Chord alignment is based on exact character positions
* Metadata is normalized and mapped to supported formats
* Unknown metadata is preserved as comments (ChordPro)

---
