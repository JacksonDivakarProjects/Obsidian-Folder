


Perfect. Let's structure the answer in **clear, separate Obsidian-friendly markdown topics** (with `##` headers) for your notes — covering:

1. Installing tools
    
2. Exporting Firefox cookies
    
3. Downloading all **video formats**
    
4. Downloading all **audio formats**
    
5. Downloading **merged (best) formats**
    
6. Output customization
    
7. Bonus: Playlist-specific commands
    

---

````markdown
# 🎥 YouTube Downloading with yt-dlp + Firefox Cookies

---

## ✅ 1. Install yt-dlp and ffmpeg

```bash
# Install latest yt-dlp binary
sudo curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
sudo chmod a+rx /usr/local/bin/yt-dlp

# Install ffmpeg for audio/video processing
sudo apt install ffmpeg
````

---

## 🔐 2. Export Firefox Cookies

1. Install Firefox Extension: [cookies.txt exporter](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)
    
2. Log in to YouTube in Firefox.
    
3. Click the extension → export cookies.
    
4. Save the file as: `cookies.txt`
    
5. Move it to your working directory or note its full path.
    

---

## 📺 3. Download All Video-Only Formats

This fetches **every video-only stream** for a given video/playlist (no audio):

```bash
yt-dlp --cookies cookies.txt -f "bv*" --allow-unplayable-formats "<playlist_or_video_url>"
```

> `bv*` = best video-only formats  
> `--allow-unplayable-formats` = fetch even DRM/unavailable formats (won't work without login)

---

## 🎵 4. Download All Audio-Only Formats

This fetches **all audio formats** separately:

```bash
yt-dlp --cookies cookies.txt -f "ba*" "<playlist_or_video_url>"
```

> `ba*` = best audio-only formats (includes multiple bitrate options)

To convert to mp3:

```bash
yt-dlp --cookies cookies.txt -x --audio-format mp3 "<playlist_or_video_url>"
```

---

## 🧩 5. Download Best Video + Audio Merged Format

```bash
yt-dlp --cookies cookies.txt -f "bv*+ba" "<playlist_or_video_url>"
```

> `bv*+ba`: download best video and best audio, then merge into a single file

---

## 🗂️ 6. Output File Format Customization

You can organize downloads using variables:

```bash
yt-dlp --cookies cookies.txt -o "~/Downloads/yt/%(playlist_title)s/%(playlist_index)s - %(title)s - %(format_id)s.%(ext)s" "<playlist_url>"
```

**Variables:**

- `%(title)s`: video title
    
- `%(format_id)s`: format number
    
- `%(playlist_index)s`: order in playlist
    
- `%(ext)s`: file extension (e.g. mp4, webm)
    

---

## 📃 7. Playlist Handling

- **Download full playlist:**
    

```bash
yt-dlp --cookies cookies.txt "<playlist_url>"
```

- **Start from a specific video index:**
    

```bash
yt-dlp --cookies cookies.txt --playlist-start 5 "<playlist_url>"
```

- **Download specific videos (e.g., 1, 3, 5–7):**
    

```bash
yt-dlp --cookies cookies.txt --playlist-items 1,3,5-7 "<playlist_url>"
```

- **Download titles and metadata only:**
    

```bash
yt-dlp --cookies cookies.txt --skip-download --print "%(title)s" "<playlist_url>"
```

---

## 💡 Tip: Resume Any Interrupted Download

```bash
yt-dlp --cookies cookies.txt -c "<playlist_or_video_url>"
```

---

## 📌 Summary Table

|Task|Command|
|---|---|
|All video formats|`-f "bv*"`|
|All audio formats|`-f "ba*"`|
|Best video+audio|`-f "bv*+ba"`|
|All formats (huge)|`--all-formats`|
|Convert to mp3|`-x --audio-format mp3`|
|Use Firefox cookies|`--cookies cookies.txt`|

---

```
yt-dlp --cookies ~/Downloads/cookies.txt \
-o "~/Downloads/yt_dsa_playlist/%(playlist_index)s - %(title)s - %(format_id)s.%(ext)s" \
"https://youtube.com/playlist?list=PLgUwDviBIf0pOd5zvVVSzgpo6BaCpHT9c&si=bD8EPK4LriBf3Zeh"


```