#!/usr/bin/env python3
# djay_playlist_to_apple_music.py
#
# djay -> Apple Music BPM + Comments sync (playlist-scoped), using VERIFIED key mapping (Djay Pro Index to Camelot).
#
# Reads BPM/key from:
#   1) secondaryIndex_mediaItemIndex (preferred)
#   2) database2 collection 'mediaItemAnalyzedData' (fallback)
#
# Includes skipped-track reporting (stdout + CSV), and tags each row with the source used.

import argparse
import csv
import sqlite3
import struct
import subprocess
from typing import Optional, List, Tuple, Dict, Any

KEY_MAP: Dict[int, str] = {
    0:  "8B - C - 1d",
    1:  "8A - A - 1m",
    2:  "3B - C# - 8d",
    3:  "3A - A# - 8m",
    4:  "10B - D - 3d",
    5:  "10A - B - 3m",
    6:  "5B - Eb / D# - 10d",
    7:  "5A - C - 10m",
    8:  "12B - E - 5d",
    9:  "12A - Dbm - 5m",
    10: "7B - F - 12d",
    11: "7A - D - 12m",
    12: "2B - F# / Gb - 7d",
    13: "2A - Ebm - 7m",
    14: "9B - G - 2d",
    15: "9A - E - 2m",
    16: "4B - Ab / G# - 9d",
    17: "4A - F - 9m",
    18: "11B - A - 4d",
    19: "11A - F# / Gb - 4m",
    20: "6B - Bb / A# - 11d",
    21: "6A - G - 11m",
    22: "1B - B - 6d",
    23: "1A - Abm - 6m",
}

BPM_MARKER = b"\x08bpm\x00"
KEYSIG_MARKER = b"\x08keySignatureIndex\x00"

def value_before_key(blob: bytes, key: str) -> Optional[str]:
    k = key.encode("utf-8")
    pos = blob.find(k)
    if pos < 0:
        return None
    end = blob.rfind(b"\x00", 0, pos)
    if end < 0:
        return None
    start = blob.rfind(b"\x08", 0, end)
    if start < 0:
        return None
    start += 1
    try:
        return blob[start:end].decode("utf-8")
    except Exception:
        return None

def list_playlists(con: sqlite3.Connection) -> List[Tuple[str, str]]:
    cur = con.cursor()
    cur.execute("SELECT key, data FROM database2 WHERE collection='mediaItemPlaylists'")
    out: List[Tuple[str, str]] = []
    for playlist_uuid, blob in cur.fetchall():
        name = value_before_key(blob, "name")
        if name and playlist_uuid != "mediaItemPlaylist-root":
            out.append((playlist_uuid, name))
    return sorted(out, key=lambda x: x[1].lower())

def playlist_uuid_by_name(con: sqlite3.Connection, playlist_name: str) -> Optional[str]:
    for puuid, name in list_playlists(con):
        if name == playlist_name:
            return puuid
    return None

def tracks_in_playlist(con: sqlite3.Connection, playlist_uuid: str) -> List[str]:
    cur = con.cursor()
    cur.execute("SELECT data FROM database2 WHERE collection='mediaItemPlaylistItems'")
    ids: List[str] = []
    for (blob,) in cur.fetchall():
        pu = value_before_key(blob, "playlistUUID")
        if pu == playlist_uuid:
            tid = value_before_key(blob, "mediaItemUUID")
            if tid:
                ids.append(tid)
    return ids

def parse_media_item_analyzed_data(blob: bytes) -> Tuple[Optional[float], Optional[int]]:
    """
    Parse bpm (float32 LE) and keySignatureIndex (0..23) from database2.mediaItemAnalyzedData blob.

    djay appears to use a compact TLV-like encoding:
      <value bytes> 0x08 <fieldName> 0x00 <type/value bytes> ...

    For keySignatureIndex we have observed at least two encodings:
      A) ... 0x0F <keyByte> 0x08 "keySignatureIndex" 0x00 ...
         (key byte is immediately BEFORE the marker, after a 0x0F tag)
      B) ... 0x08 "keySignatureIndex" 0x00 <keyByte> 0x08 "isStraight" 0x00 ...
         (key byte is immediately AFTER the marker)

    This parser tries, in order:
      1) byte immediately AFTER the marker (if 0..23)
      2) byte immediately BEFORE the marker (if 0..23)
      3) scan a small window before the marker for 0x0F and use the following byte (if 0..23)
    """
    bpm: Optional[float] = None
    key_sig: Optional[int] = None

    # BPM: float32 immediately BEFORE marker: 0x08 'bpm' 0x00
    p = blob.find(BPM_MARKER)
    if p >= 4:
        try:
            bpm = struct.unpack("<f", blob[p - 4 : p])[0]
        except Exception:
            bpm = None

    ks = blob.find(KEYSIG_MARKER)
    if ks >= 0:
        after = ks + len(KEYSIG_MARKER)
        if after < len(blob):
            cand_after = blob[after]
            if 0 <= cand_after <= 23:
                key_sig = int(cand_after)

        if key_sig is None and ks >= 1:
            cand_before = blob[ks - 1]
            if 0 <= cand_before <= 23:
                key_sig = int(cand_before)

        if key_sig is None:
            start = max(0, ks - 32)
            window = blob[start:ks]
            idx = window.rfind(b"\x0f")
            if idx >= 0 and (start + idx + 1) < ks:
                cand2 = blob[start + idx + 1]
                if 0 <= cand2 <= 23:
                    key_sig = int(cand2)

    return bpm, key_sig



def get_bpm_keyindex(con: sqlite3.Connection, title_id: str) -> Tuple[Optional[float], Optional[int], str]:
    cur = con.cursor()
    cur.execute(
        "SELECT bpm, musicalKeySignatureIndex FROM secondaryIndex_mediaItemIndex WHERE titleID=?",
        (title_id,),
    )
    row = cur.fetchone()
    if row and (row[0] is not None or row[1] is not None):
        bpm, key_idx = row[0], row[1]
        key_idx_int = int(key_idx) if key_idx is not None else None
        return bpm, key_idx_int, "secondaryIndex_mediaItemIndex"

    cur.execute(
        "SELECT data FROM database2 WHERE collection='mediaItemAnalyzedData' AND key=?",
        (title_id,),
    )
    r2 = cur.fetchone()
    if not r2:
        return None, None, "none"

    bpm2, key2 = parse_media_item_analyzed_data(r2[0])
    if bpm2 is None and key2 is None:
        return None, None, "none"
    return bpm2, key2, "mediaItemAnalyzedData"

def get_track_metadata(con: sqlite3.Connection, title_id: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    cur = con.cursor()
    cur.execute(
        "SELECT data FROM database2 WHERE collection='mediaItems' AND key=?",
        (title_id,),
    )
    row = cur.fetchone()
    if not row:
        return None, None, None

    blob = row[0]
    title = value_before_key(blob, "title")
    artist = value_before_key(blob, "artist")
    album_id = value_before_key(blob, "album")

    album_name = None
    if album_id:
        cur.execute(
            "SELECT data FROM database2 WHERE collection='mediaAlbums' AND key=?",
            (album_id,),
        )
        arow = cur.fetchone()
        if arow:
            album_name = value_before_key(arow[0], "name")

    return title, artist, album_name

def _esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')

def applescript_update_track(
    title: str,
    artist: str,
    album: Optional[str],
    bpm: Optional[int],
    comment: Optional[str],
    no_overwrite: bool,
    update_all_matches: bool,
) -> str:
    title_s = _esc(title)
    artist_s = _esc(artist)
    album_clause = f' and album is "{_esc(album)}"' if album else ""

    bpm_line = f"set bpm of t to {int(bpm)}" if bpm is not None else ""
    cmt_line = f'set comment of t to "{_esc(comment)}"' if comment else ""

    if no_overwrite:
        bpm_set = f'if (bpm of t is 0) then {bpm_line} end if' if bpm_line else ""
        cmt_set = f'if (comment of t is \"") then {cmt_line} end if' if cmt_line else ""
    else:
        bpm_set = bpm_line
        cmt_set = cmt_line

    update_block = f"{bpm_set}\n{cmt_set}".strip()
    if not update_block:
        return "SKIP: no djay values"

    if update_all_matches:
        script_text = f'''
        tell application "Music"
          try
            set matches to (every track of library playlist 1 whose name is "{title_s}" and artist is "{artist_s}"{album_clause})
            set n to (count of matches)
            if n is 0 then return "NOTFOUND"
            repeat with t in matches
              {update_block}
            end repeat
            return "OK:" & n
          on error errMsg number errNum
            return "ERR " & errNum & ": " & errMsg
          end try
        end tell
        '''
    else:
        script_text = f'''
        tell application "Music"
          try
            set matches to (every track of library playlist 1 whose name is "{title_s}" and artist is "{artist_s}"{album_clause})
            set n to (count of matches)
            if n is 0 then
              return "NOTFOUND"
            else if n is not 1 then
              return "AMBIGUOUS:" & n
            end if
            set t to item 1 of matches
            {update_block}
            return "OK"
          on error errMsg number errNum
            return "ERR " & errNum & ": " & errMsg
          end try
        end tell
        '''

    p = subprocess.run(["osascript", "-e", script_text], capture_output=True, text=True)
    return (p.stdout or p.stderr).strip()

def write_csv(rows: List[Dict[str, Any]], csv_path: str) -> None:
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["artist", "title", "album", "titleID", "bpm_raw", "key_idx", "derived_key", "source"])
        for t in rows:
            w.writerow([
                t["artist"],
                t["title"],
                t["album"] or "",
                t["title_id"],
                "" if t["bpm_raw"] is None else t["bpm_raw"],
                "" if t["key_idx"] is None else t["key_idx"],
                "" if t["comment"] is None else t["comment"],
                t["source"],
            ])

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True, help="Path to djay MediaLibrary.db")
    ap.add_argument("--list-playlists", action="store_true")
    ap.add_argument("--playlist", help="Exact djay playlist name to use")
    ap.add_argument("--limit", type=int, default=0, help="Limit number of tracks (0 = no limit)")
    ap.add_argument("--apply", action="store_true", help="Write to Apple Music (otherwise dry-run)")
    ap.add_argument("--no-overwrite", action="store_true", help="Fill blanks only (do not overwrite).")
    ap.add_argument("--update-all-matches", action="store_true",
                    help="If multiple matches exist in Apple Music, update all of them (use with care).")
    ap.add_argument("--verbose", action="store_true", help="Print per-track status during --apply.")
    ap.add_argument("--report-skipped", action="store_true", help="Print skipped track report.")
    ap.add_argument("--report-limit", type=int, default=50, help="Limit printed skipped rows (0 = no limit).")
    ap.add_argument("--report-skipped-csv", default="", help="Write skipped report CSV to this path.")
    ap.add_argument("--report-all-csv", default="", help="Write full report CSV to this path.")
    args = ap.parse_args()

    con = sqlite3.connect(args.db)

    if args.list_playlists:
        for _, name in list_playlists(con):
            print(name)
        return

    if not args.playlist:
        raise SystemExit("Provide --playlist or use --list-playlists")

    puuid = playlist_uuid_by_name(con, args.playlist)
    if not puuid:
        raise SystemExit(f"Playlist not found: {args.playlist}")

    ids = tracks_in_playlist(con, puuid)
    if args.limit and args.limit > 0:
        ids = ids[: args.limit]

    planned: List[Dict[str, Any]] = []
    for tid in ids:
        bpm_raw, key_idx, source = get_bpm_keyindex(con, tid)
        title, artist, album = get_track_metadata(con, tid)
        if not title or not artist:
            continue

        if bpm_raw is None:
            bpm_int = None
        else:
            try:
                bpm_int = int(round(float(bpm_raw)))
            except Exception:
                bpm_int = None

        comment = KEY_MAP.get(key_idx) if key_idx is not None else None

        planned.append({
            "title": title,
            "artist": artist,
            "album": album,
            "title_id": tid,
            "bpm_raw": bpm_raw,
            "bpm_int": bpm_int,
            "key_idx": key_idx,
            "comment": comment,
            "source": source,
        })

    print(f"Playlist: {args.playlist}")
    print(f"Tracks found (with title+artist): {len(planned)}")
    print("Preview (first 25):")
    for t in planned[:25]:
        print(
            f"- {t['artist']} — {t['title']} | album={t['album']} | "
            f"bpm={t['bpm_int']} | djKeyIdx={t['key_idx']} | comment='{t['comment']}' | src={t['source']}"
        )

    skipped = [t for t in planned if t["bpm_int"] is None and t["comment"] is None]

    if args.report_skipped:
        print("\n--- SKIPPED TRACK DETAIL REPORT ---")
        print(f"Skipped tracks: {len(skipped)}\n")
        rows = skipped if args.report_limit == 0 else skipped[: args.report_limit]
        for t in rows:
            print(
                f"{t['artist']} — {t['title']}\n"
                f"  titleID: {t['title_id']}\n"
                f"  bpm_raw: {t['bpm_raw']}\n"
                f"  key_idx: {t['key_idx']}\n"
                f"  derived_key: {t['comment']}\n"
                f"  source: {t['source']}\n"
            )

    if args.report_skipped_csv:
        write_csv(skipped, args.report_skipped_csv)
        print(f"Wrote skipped CSV: {args.report_skipped_csv}")

    if args.report_all_csv:
        write_csv(planned, args.report_all_csv)
        print(f"Wrote full CSV: {args.report_all_csv}")

    if not args.apply:
        print("\nDry run only. Re-run with --apply to write to Apple Music.")
        return

    stats = {"OK": 0, "OK_MULTI": 0, "AMBIGUOUS": 0, "NOTFOUND": 0, "SKIP": 0, "ERR": 0}

    for t in planned:
        if t["bpm_int"] is None and t["comment"] is None:
            res = "SKIP: no djay values"
        else:
            res = applescript_update_track(
                title=t["title"],
                artist=t["artist"],
                album=t["album"],
                bpm=t["bpm_int"],
                comment=t["comment"],
                no_overwrite=args.no_overwrite,
                update_all_matches=args.update_all_matches,
            )

        if args.verbose:
            print(f"{res} | {t['artist']} — {t['title']} | src={t['source']}")

        if res == "OK":
            stats["OK"] += 1
        elif res.startswith("OK:"):
            stats["OK_MULTI"] += 1
        elif res.startswith("AMBIGUOUS:"):
            stats["AMBIGUOUS"] += 1
        elif res.startswith("NOTFOUND"):
            stats["NOTFOUND"] += 1
        elif res.startswith("SKIP"):
            stats["SKIP"] += 1
        else:
            stats["ERR"] += 1

    print("Done. Summary:", stats)

if __name__ == "__main__":
    main()
