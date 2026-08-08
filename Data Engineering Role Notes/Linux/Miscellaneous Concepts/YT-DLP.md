# 🎥 YouTube Downloading With `yt-dlp` + Firefox Cookies

Covers: installing the tools, exporting Firefox cookies, downloading video-only/audio-only/merged formats, customizing output filenames, and playlist-specific options.

## ✅ 1. Install `yt-dlp` and `ffmpeg`

```bash
# Install latest yt-dlp binary
sudo curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
sudo chmod a+rx /usr/local/bin/yt-dlp

# Install ffmpeg for audio/video merging and conversion
sudo apt install ffmpeg
```

## 🔐 2. Export Firefox Cookies

1. Install the Firefox extension: [cookies.txt exporter](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)
2. Log in to YouTube in Firefox.
3. Click the extension → export cookies.
4. Save the file as `cookies.txt`.
5. Move it to your working directory, or note its full path — you'll pass it via `--cookies`.

Cookies are needed for age-restricted, members-only, or otherwise login-gated content.

## 📺 3. Download All Video-Only Formats

```bash
yt-dlp --cookies cookies.txt -f "bv*" --allow-unplayable-formats "<playlist_or_video_url>"
```
- `bv*` = best video-only formats
- `--allow-unplayable-formats` = also list/fetch formats yt-dlp would normally hide as unplayable (e.g. DRM-protected); won't succeed without valid login/cookies

## 🎵 4. Download All Audio-Only Formats

```bash
yt-dlp --cookies cookies.txt -f "ba*" "<playlist_or_video_url>"
```
- `ba*` = best audio-only formats (includes multiple bitrate options)

To convert to mp3:
```bash
yt-dlp --cookies cookies.txt -x --audio-format mp3 "<playlist_or_video_url>"
```

## 🧩 5. Download Best Video + Audio, Merged

```bash
yt-dlp --cookies cookies.txt -f "bv*+ba" "<playlist_or_video_url>"
```
`bv*+ba` downloads the best video-only and best audio-only streams separately, then merges them into one file (requires `ffmpeg`).

## 🗂️ 6. Output Filename Customization

```bash
yt-dlp --cookies cookies.txt -o "~/Downloads/yt/%(playlist_title)s/%(playlist_index)s - %(title)s - %(format_id)s.%(ext)s" "<playlist_url>"
```

**Variables:**
- `%(title)s` — video title
- `%(format_id)s` — format identifier
- `%(playlist_index)s` — position within the playlist
- `%(ext)s` — file extension (e.g. mp4, webm)

## 📃 7. Playlist Handling

Download the full playlist:
```bash
yt-dlp --cookies cookies.txt "<playlist_url>"
```

Start from a specific index:
```bash
yt-dlp --cookies cookies.txt --playlist-start 5 "<playlist_url>"
```

Download specific items (e.g. 1, 3, 5–7):
```bash
yt-dlp --cookies cookies.txt --playlist-items 1,3,5-7 "<playlist_url>"
```

Titles/metadata only, no download:
```bash
yt-dlp --cookies cookies.txt --skip-download --print "%(title)s" "<playlist_url>"
```

## 💡 Tip: Resume an Interrupted Download

```bash
yt-dlp --cookies cookies.txt -c "<playlist_or_video_url>"
```

## 📌 Summary Table

| Task | Command |
|---|---|
| All video formats | `-f "bv*"` |
| All audio formats | `-f "ba*"` |
| Best video+audio | `-f "bv*+ba"` |
| All formats (huge) | `--all-formats` |
| Convert to mp3 | `-x --audio-format mp3` |
| Use Firefox cookies | `--cookies cookies.txt` |

## Worked Example

```bash
yt-dlp --cookies ~/Downloads/cookies.txt \
-o "~/Downloads/yt_dsa_playlist/%(playlist_index)s - %(title)s - %(format_id)s.%(ext)s" \
"https://youtube.com/playlist?list=PLgUwDviBIf0pOd5zvVVSzgpo6BaCpHT9c&si=bD8EPK4LriBf3Zeh"
```

## 🔗 Related Notes
- [[Data Engineering Role Notes/Linux/Miscellaneous Concepts/Linux Clear Cache|Linux Clear Cache]]
