#!/usr/bin/env python3
import sys
import os
import tempfile
import gdown

FILE_ID = "1o-LGPQr-ML6xSp4hmTGGuGZO2pyWBLk5"

def log(msg):
    # stderr only — never contaminate stdout
    print(msg, file=sys.stderr)

def main():
    fd, tmp_path = tempfile.mkstemp(suffix=".parquet")
    os.close(fd)

    try:
        log(f"Downloading file_id={FILE_ID} to temp path")
        # quiet=True to guarantee no progress bar leaks into stdout
        result = gdown.download(id=FILE_ID, output=tmp_path, quiet=True)

        if result is None:
            log("gdown.download returned None — download failed")
            sys.exit(1)

        with open(tmp_path, "rb") as f:
            data = f.read()

        if data[:4] != b"PAR1":
            log("Downloaded file does not look like valid Parquet (bad magic bytes)")
            sys.exit(1)

        sys.stdout.buffer.write(data)

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    main()