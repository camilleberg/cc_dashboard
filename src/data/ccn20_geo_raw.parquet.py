#!/usr/bin/env python3
import sys
import os
import shutil
import tempfile
import time
import gdown

FILE_ID = "1o-LGPQr-ML6xSp4hmTGGuGZO2pyWBLk5"

# Where downloaded raw files are cached between loader runs.
# Adjust CACHE_DIR if you want this somewhere else (e.g. next to your data/ folder).
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")
CACHE_PATH = os.path.join(CACHE_DIR, f"{FILE_ID}.parquet")

# How long a cached download is considered fresh before re-downloading.
# Override with env var if you want to force a refresh cadence, e.g. CACHE_TTL_SECONDS=0
CACHE_TTL_SECONDS = int(os.environ.get("CACHE_TTL_SECONDS", 60 * 60 * 6))  # 6 hours


def log(msg):
    # stderr only — never contaminate stdout
    print(msg, file=sys.stderr)


def is_valid_parquet(path):
    try:
        with open(path, "rb") as f:
            return f.read(4) == b"PAR1"
    except OSError:
        return False


def cache_is_fresh(path):
    if not os.path.exists(path):
        return False
    if not is_valid_parquet(path):
        return False
    age = time.time() - os.path.getmtime(path)
    return age < CACHE_TTL_SECONDS


def download_to_cache():
    os.makedirs(CACHE_DIR, exist_ok=True)

    # Download to a temp file first, then atomically move into place.
    # Avoids ever leaving a half-written file at CACHE_PATH.
    fd, tmp_path = tempfile.mkstemp(suffix=".parquet", dir=CACHE_DIR)
    os.close(fd)

    try:
        log(f"Downloading file_id={FILE_ID}")
        result = gdown.download(id=FILE_ID, output=tmp_path, quiet=True)

        if result is None:
            log("gdown.download returned None — download failed")
            sys.exit(1)

        if not is_valid_parquet(tmp_path):
            log("Downloaded file does not look like valid Parquet (bad magic bytes)")
            sys.exit(1)

        os.replace(tmp_path, CACHE_PATH)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def main():
    if not cache_is_fresh(CACHE_PATH):
        download_to_cache()
    else:
        log(f"Using cached download ({CACHE_PATH})")

    # No transform is currently applied, so just stream the bytes straight
    # through — this skips a full parquet decode/encode round-trip via pandas.
    # If/when you re-enable the geometry transform below, read+process only
    # in that branch so the pass-through path stays fast.
    #
    # import pandas as pd, shapely
    # df = pd.read_parquet(CACHE_PATH)
    # df["geometry"] = shapely.to_geojson(shapely.from_wkb(df["geometry"]))
    # sys.stdout.buffer.write(df.to_parquet(index=False))
    # return

    with open(CACHE_PATH, "rb") as f:
        shutil.copyfileobj(f, sys.stdout.buffer)


if __name__ == "__main__":
    main()