import re
import os
import sys
import json
import hashlib
import threading
import traceback
import subprocess
import google_music
import concurrent.futures

state_file = "state.json"
with open(state_file, "r") as f:
	state = json.load(f)

if not state["uploader_id"]:
	print("ERROR: no uploader_id specified")
	exit(1)

lock = threading.Lock()
executor = concurrent.futures.ThreadPoolExecutor(max_workers=8)
mm = google_music.musicmanager(uploader_id=state["uploader_id"])

def sync(song, cover):
	try:
		if song in state["song_id_mapping"]:
			print(f"skipped: {song}")
			return

		print(f"uploading: {song}")
		sync_action(song, cover)
	except:
		traceback.print_exc()

def dryrun(song, cover):
	print(f"DRYRUN: {song}")

def upload(song, cover):
	key = hashlib.sha512(song.encode("utf-8")).hexdigest()
	tmpSong = f"/tmp/{key}.mp3"
	tmpCover = None

	if cover is None:
		print(f"NOTICE: using embedded cover art for {song}")
		cover = tmpCover = f"/tmp/{key}.jpg"
		subprocess.run(["ffmpeg", "-y", "-i", song, "-an", "-c:v", "copy", tmpCover], stderr=subprocess.DEVNULL)

	subprocess.run(["ffmpeg", "-y", "-i", song, "-c:a", "libmp3lame", "-b:a", "320k", tmpSong], stderr=subprocess.DEVNULL)
	result = mm.upload(tmpSong, album_art_path=cover, no_sample=True)
	print(f"{result['reason']}: {song}")

	os.unlink(tmpSong)
	if tmpCover is not None:
		os.unlink(tmpCover)

	if result["reason"] in ("Uploaded", "ALREADY_EXISTS"):
		with lock:
			state["song_id_mapping"][song] = result["song_id"]
			with open(state_file, "w") as f:
				json.dump(state, f, indent="\t", sort_keys=True, ensure_ascii=False)

sync_action = dryrun
if len(sys.argv) > 1 and sys.argv[1] == "--doit":
	sync_action = upload

for pwd, dirs, files in os.walk("./library"):
	songs = [f for f in files if re.search("\.(flac|mp3)$", f)]
	if len(songs) == 0:
		continue

	cover = [f for f in files if re.search("\.(jpe?g|png)$", f)]
	if len(cover) == 0:
		print(f"WARN: No cover arts were found at {pwd}")
	elif len(cover) > 1:
		print(f"WARN: More than one cover arts were found at {pwd} ({cover[0]} will be used)")

	for song in songs:
		executor.submit(sync, f"{pwd}/{song}", f"{pwd}/{cover[0]}" if len(cover) > 0 else None)
