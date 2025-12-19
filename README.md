# djay-pro-keys-to-apple-music
A python script to set BPM and Key Values to tracks in Apple Music.

## Djay Pro

1. Connect Apple Music to Djay Pro
2. Find Playlist in Djay Pro
3. Analyze all songs in Playlist
4. Add Apple Music Playlist to Djay Pro’s Playlists

## Finder
1. Find DJ Pro package in Finder
2. Show Package Contents
3. Copy the three DJ Pro Database files
4. Make a new File Folder. For example, “djay db to Apple Music”
5. Paste the three DJ Pro Database files into your new File Folder

## Terminal (Python Script)

1. Open Terminal
2. Go to directory “djay db to Apple Music”
3. Run djay_playlist_to_apple_music.py as follows:
    
    ```jsx
    python3 djay_playlist_to_apple_music.py \
      --db "MediaLibrary.db" \
      --playlist "NAME" \
      --apply
    ```
    
    1. Set DB filename: `MediaLibrary.db`
    2. Select Playlist to export. Update `NAME` 
    3. Include Apply command to append Apple Music `--apply` or 
    4. Include No Overwrite command to only update blank BPM and Comment fields `--no-overwrite`

## Additional script variables and tools

`-- report-all-csv "FILENAME.csv"`

`-- report-skipped-csv "FILENAME.csv"`

`-- no-overwrite` (for existing BPM and Comment field data to not be replaced)

`-- list-playlists` (to list out all Playlists available in the Djay Pro database)

`-- limit #` (replace the # to set a limit)

## Apple Music

Watch as the Apple Music playlist is automagically updated.

🔥 Updating a thousand songs takes less than 5 minutes.
