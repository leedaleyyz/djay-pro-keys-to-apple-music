# Introducing djay-pro-keys-to-apple-music
A python script to set BPM and Key Values to tracks in Apple Music so you can easily create harmonic playlists in Apple Music.

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

Once you have the all the key data for the tracks, switch your Playlist to View, as Songs in Apple Music, and reveal the BPM and Comments fields in the available columns.

Start with your favourite first track for the playlist, and then use the [Camelot wheel](https://dj.studio/blog/camelot-wheel) to sequence the rest of the playlist with intention.

I guarantee your playlists have never sounded better!

## What would a DJ use this for?
If your day-to-day music discovery service is Apple Music and you make Playlists in Apple Music based on genre, theme, sequences of songs, or upcoming mixes, now you can organize by key in Apple Music instead of having to jump into Djay Pro to manage all your playlists there.

# Workflow for djay-pro-keys-to-apple-music

## Djay Pro

1. Connect Apple Music to Djay Pro
2. Find Playlist in Djay Pro
3. Analyze all songs in Playlist
4. Add Apple Music Playlist to Djay Pro’s Playlists

## Finder
1. Find Djay Pro package in Finder
2. Show Package Contents
3. Copy the three Djay Pro Database files
4. Make a new File Folder. For example, “djay db to Apple Music”
5. Paste the three Djay Pro Database files into your new File Folder

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
