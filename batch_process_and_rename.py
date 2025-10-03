#!/usr/bin/env python3
"""
batch_process_and_rename.py

Batch-upload CSV files from Dataset/output/ to your Flask route /process_csv,
then locate the processed file created by the server and rename/move it to
Dataset/processed/processed_<originalname>_<timestamp>.csv

Usage:
    python batch_process_and_rename.py
    python batch_process_and_rename.py --input-dir Dataset/output --output-dir Dataset/processed --server-url http://127.0.0.1:5000/process_csv
"""

import os
import sys
import time
import glob
import shutil
import argparse
import requests
import re
from datetime import datetime

DEFAULT_INPUT_DIR = "Dataset/output"
DEFAULT_OUTPUT_DIR = "Dataset/processed"
DEFAULT_SERVER_URL = "http://127.0.0.1:5000/process_csv"
SEARCH_TIMEOUT = 30  # seconds to wait for server to write the processed file


def upload_file_to_server(file_path, server_url, timeout=600):
    """Upload the CSV to the server endpoint (multipart/form-data, field name 'file')."""
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f, "text/csv")}
        try:
            resp = requests.post(server_url, files=files, timeout=timeout)
            return resp
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"HTTP request failed: {e}")


def find_server_saved_file_from_response(resp_json):
    """
    Try to extract an 'output_file' path from JSON response.
    Also attempt to parse common message strings that contain the path.
    Returns absolute path or None.
    """
    if not resp_json:
        return None

    # 1) Preferred structured field
    if isinstance(resp_json, dict):
        output_file = resp_json.get("output_file") or resp_json.get("output_path")
        if output_file:
            return os.path.abspath(output_file)

    # 2) Try parse from message text: "saved as /path/to/file.csv" or windows path
    msg = None
    if isinstance(resp_json, dict):
        msg = resp_json.get("message") or resp_json.get("msg") or json_dumps_short(resp_json)
    else:
        try:
            msg = str(resp_json)
        except Exception:
            msg = ""

    if msg:
        # regex tries to capture windows or unix absolute path ending with .csv
        m = re.search(r'([A-Za-z]:\\(?:[^\\\s]+\\)*[^\\\s]+\.csv)|(/\S*processed\S*\.csv)', msg)
        if m:
            return os.path.abspath(m.group(0))

    return None


def json_dumps_short(obj):
    try:
        import json
        return json.dumps(obj)
    except Exception:
        return str(obj)


def find_recent_processed_file(search_dir, start_time, timeout=SEARCH_TIMEOUT, patterns=("processed_*", "processed_output.csv")):
    """
    Search `search_dir` for files matching patterns and modified after start_time.
    Waits up to `timeout` seconds for a matching file to appear.
    Returns the most recently modified matching file path or None.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        candidates = []
        for pat in patterns:
            for p in glob.glob(os.path.join(search_dir, pat)):
                try:
                    mtime = os.path.getmtime(p)
                except OSError:
                    continue
                if mtime >= start_time - 0.5:
                    candidates.append((p, mtime))
        if candidates:
            # return newest
            candidates.sort(key=lambda x: x[1], reverse=True)
            return os.path.abspath(candidates[0][0])
        time.sleep(0.5)
    return None


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def process_batch(input_dir, output_dir, server_url, verbose=True):
    input_dir = os.path.abspath(input_dir)
    output_dir = os.path.abspath(output_dir)
    cwd = os.getcwd()  # assume server writes to its working dir (project root)

    ensure_dir(output_dir)

    csv_files = sorted(glob.glob(os.path.join(input_dir, "*.csv")))
    if not csv_files:
        print(f"No CSV files found in {input_dir}")
        return

    summary = []
    for csv_path in csv_files:
        base = os.path.basename(csv_path)
        print(f"\n=== Processing: {base} ===")
        start_time = time.time()  # used to find newly created processed file
        try:
            resp = upload_file_to_server(csv_path, server_url)
        except Exception as e:
            print(f"[ERROR] Failed to upload {base}: {e}")
            summary.append((base, "upload_failed", str(e)))
            continue

        # got HTTP response - check status
        status = resp.status_code
        resp_json = None
        try:
            resp_json = resp.json()
        except Exception:
            # not JSON; keep raw text
            resp_text = resp.text

        if status != 200 and status != 201:
            print(f"[ERROR] Server returned status {status} for {base}: {resp.text}")
            summary.append((base, "server_error", f"status {status}"))
            continue

        print(f"Upload OK (status {status}). Trying to locate the server-saved processed file...")

        # 1) try to extract explicit path from JSON response
        server_saved = None
        if resp_json:
            server_saved = find_server_saved_file_from_response(resp_json)

        # 2) if not present in response, attempt to find a recently created processed file in cwd
        if not server_saved:
            server_saved = find_recent_processed_file(cwd, start_time, timeout=SEARCH_TIMEOUT)

        if not server_saved or not os.path.exists(server_saved):
            print(f"[ERROR] Could not find server-side processed file for {base}.")
            # Provide the response JSON/text so the user can debug
            try:
                print("Server response (raw):", resp_json or resp.text[:400])
            except Exception:
                pass
            summary.append((base, "no_processed_file", "not_found"))
            continue

        # move/rename server_saved -> output_dir/processed_<base>_<timestamp>.csv
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        name_wo_ext = os.path.splitext(base)[0]
        dest_name = f"processed_{name_wo_ext}_{ts}.csv"
        dest_path = os.path.join(output_dir, dest_name)

        try:
            # use move to relocate the server file to the output dir with new name
            shutil.move(server_saved, dest_path)
            print(f"Saved processed file as: {dest_path}")
            summary.append((base, "ok", dest_path))
        except Exception as e:
            print(f"[ERROR] Failed to move/rename {server_saved} -> {dest_path}: {e}")
            summary.append((base, "move_failed", str(e)))
            continue

        # small pause to let filesystem settle before next upload
        time.sleep(0.2)

    # summary
    print("\n=== Batch Summary ===")
    for s in summary:
        print(s)

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch upload CSVs to /process_csv and rename processed files.")
    parser.add_argument("--input-dir", default=DEFAULT_INPUT_DIR, help="Directory containing input CSVs")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Directory to save processed/renamed CSVs")
    parser.add_argument("--server-url", default=DEFAULT_SERVER_URL, help="Full URL of the /process_csv endpoint")
    parser.add_argument("--timeout", type=int, default=SEARCH_TIMEOUT, help="Seconds to wait for server to write processed file")
    args = parser.parse_args()

    SEARCH_TIMEOUT = args.timeout
    process_batch(args.input_dir, args.output_dir, args.server_url)
