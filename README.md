# Introducing djay-pro-keys-to-apple-music
A python script to add Djay Pro analyzed BPM and Key Values to tracks in Apple Music so you can easily create harmonic playlists in Apple Music.

## Why do you need this?
Because Apple Music has a blank BPM field as a default and no Keys for songs (you can use the Comments field to include Key data).

And because Apple Music can't analyze a song to give you the BPM and Key.

But Djay Pro can analyze songs to give you an accurate BPM and Key.

And Djay Pro allows you to connect to your Apple Music library.

But then you'd have to manually update the BPM and Comment fields for every song in Apple Music to get these into Apple Music.

So use djay-pro-keys-to-apple-music to automate updating Apple Music with the Djay Pro BPM and Key data.

## Why do the BPM and Key matter?
Well, let's say you want to put a great sounding playlist together.

Keys in particular are essential for creating playlists where one song fits like a glove with the next.

BPM helps you know if your next track will speed up or slow down the tempo from the previous, but the key will let you know if it sounds great.

By having the key data from djay-pro-keys-to-apple-music you can sequence a playlist in a way that builds naturally and sounds amazing, every time.

Once you have the all the key data for the tracks, switch your Apple Music Playlist to View, as Songs, and then reveal the BPM and Comments fields in the available columns.

Start with your favourite first track for the playlist, and then use the [Camelot wheel](https://dj.studio/blog/camelot-wheel) to sequence the rest of the playlist with intention.

I guarantee your playlists will sound better than ever!

## What would a DJ use this for?
If your day-to-day music discovery service is Apple Music and you make Playlists in Apple Music based on genre, theme, sequences of songs, or upcoming mixes, now you can organize by key in Apple Music instead of having to jump into Djay Pro to manage all your playlists.

# Workflow for djay-pro-keys-to-apple-music
**Important: playlists must exist as local djay Pro playlists**

This script does not read Apple Music playlists directly.

It reads playlist data from djay Pro’s local MediaLibrary.db. That means any Apple Music playlist you want to process must first be copied or added into djay Pro’s own playlist library.

If a playlist exists only in Apple Music, the script will not find it and may return:
    ```Playlist not found: PLAYLIST NAME```

Before running the script, confirm the playlist appears under djay Pro’s local playlists, not only under the Apple Music source inside djay.

## Djay Pro

1. Connect Apple Music to djay Pro.
2. In djay Pro, find the Apple Music playlist you want to process.
3. Copy or add that Apple Music playlist into djay Pro’s local playlists.
4. Open the copied djay Pro playlist.
5. Analyze all songs in that djay Pro playlist.
6. Confirm BPM and Key values are visible in djay Pro.
7. Quit djay Pro, or make sure the database files are fully written before copying them.

## Finder
1. Find the Djay Pro package in Finder
2. Show Package Contents
3. Copy the three Djay Pro Database files
4. Make a new File Folder. For example, “djay db to Apple Music”
5. Paste the three Djay Pro Database files into your new File Folder
6. Copy the script, "djay-pro-keys-to-apple-music.py" to this same File Folder

## Terminal (Python Script)

1. Open Terminal
2. Go to the directory with the database files and the script. ie, “djay db to Apple Music”
3. Run djay_playlist_to_apple_music.py as follows:
    
    ```jsx
    python3 djay_playlist_to_apple_music.py \
      --db "MediaLibrary.db" \
      --playlist "NAME" \
      --apply
    ```
    
    1. Set DB filename: `MediaLibrary.db`
    2. Select Playlist to export: Update `NAME` to the name of one of the playlists you added as a Djay Pro playlist.
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
