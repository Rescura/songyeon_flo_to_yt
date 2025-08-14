

import re
import sys

# The script will read the file "새 텍스트 문서.txt" from the absolute path with forward slashes.
with open("C:/Users/ayj604516/OneDrive/연애/FlotoYTMusic/새 텍스트 문서.txt", 'r', encoding='utf-8') as f:
    content = f.read()

pattern = re.compile(r"'[^']+' 앨범 이미지\s*\n\s*(.*?)\s*\n\s*.*?\s*\n\s*(.*?)\s*\n\s*선택한 음악 듣기", re.MULTILINE)

matches = pattern.findall(content)

seen = set()

with open("C:/Users/ayj604516/OneDrive/연애/FlotoYTMusic/playlist.txt", 'w', encoding='utf-8') as out_file:
    for match in matches:
        title = match[0].strip()
        artist = match[1].strip()

        if len(artist) > 40:
            continue

        if artist and title:
            title = re.sub(r'\s*\(feat.*?\)', '', title, flags=re.IGNORECASE)
            title = re.sub(r'\s*\(explicit ver\.\)', '', title, flags=re.IGNORECASE)
            title = title.strip()

            song_entry = f"{artist} - {title}"
            if song_entry not in seen:
                out_file.write(song_entry + '\n')
                seen.add(song_entry)

