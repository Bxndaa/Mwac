"""Read-only checks for a Drive -> Frame.io pilot in a Codex Cloud task.

No uploads, changes to permissions, deletion, or scheduler creation.
"""
import argparse
import json
import os
import re
import shutil
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def identifier(value, field):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_:|.-]+", value):
        raise ValueError(f"Invalid or missing {field}")
    if value.startswith("REPLACE_"):
        raise ValueError(f"Configure {field} before the pilot")
    return value


def validate(config):
    identifier(config.get("frame_account_id"), "frame_account_id")
    routes = config.get("routes")
    if not isinstance(routes, list) or not routes:
        raise ValueError("Configure at least one explicit folder mapping")
    seen = set()
    for route in routes:
        source = identifier(route.get("drive_folder_id"), "drive_folder_id")
        identifier(route.get("frame_folder_id"), "frame_folder_id")
        if source in seen:
            raise ValueError("A Drive folder must have exactly one destination")
        seen.add(source)
    maximum = config.get("max_file_bytes")
    reserve = config.get("reserve_bytes")
    if type(maximum) is not int or maximum <= 0:
        raise ValueError("max_file_bytes must be a positive integer")
    if type(reserve) is not int or reserve < 0:
        raise ValueError("reserve_bytes must be a non-negative integer")
    return config


def get_json(url, token):
    # Fixed API hosts only; redirects would risk forwarding Authorization.
    if not url.startswith(("https://www.googleapis.com/", "https://api.frame.io/")):
        raise ValueError("Unsupported API destination")
    request = Request(url, headers={"Authorization": "Bearer " + token})
    try:
        with build_opener(NoRedirect).open(request, timeout=30) as response:
            return json.load(response)
    except HTTPError as error:
        # Do not expose response bodies, tokens, or signed URLs in diagnostics.
        raise RuntimeError(f"API returned HTTP {error.code}") from None
    except URLError:
        raise RuntimeError("API is unreachable from this environment") from None


def inspect(config, *, offline=False):
    config = validate(config)
    disk = shutil.disk_usage(Path.cwd())
    report = {
        "read_only": True,
        "offline": offline,
        "disk_total_bytes": disk.total,
        "disk_free_bytes": disk.free,
        "requested_max_file_bytes": config["max_file_bytes"],
        "space_for_one_file": disk.free >= config["max_file_bytes"] + config["reserve_bytes"],
        "routes": [],
        "not_tested": ["upload", "cleanup", "oauth_refresh", "durable_history", "cloud_schedule"],
    }
    if offline:
        return report
    drive_token = os.environ.get("ENGRAME_DRIVE_ACCESS_TOKEN")
    frame_token = os.environ.get("ENGRAME_FRAME_ACCESS_TOKEN")
    if not drive_token or not frame_token:
        raise ValueError("Add both access-token keys in the Codex Cloud vault for this read-only test")
    account = quote(config["frame_account_id"], safe="")
    for route in config["routes"]:
        source = quote(route["drive_folder_id"], safe="")
        target = quote(route["frame_folder_id"], safe="")
        folder = get_json(
            f"https://www.googleapis.com/drive/v3/files/{source}?" + urlencode({
                "supportsAllDrives": "true", "fields": "id,mimeType,capabilities(canListChildren,canTrashChildren)"
            }), drive_token,
        )
        if folder.get("mimeType") != "application/vnd.google-apps.folder":
            raise ValueError("Drive source is not a folder")
        dest = get_json(f"https://api.frame.io/v4/accounts/{account}/folders/{target}", frame_token)
        if dest.get("data", {}).get("type") != "folder":
            raise ValueError("Frame.io destination is not a folder")
        sample = get_json("https://www.googleapis.com/drive/v3/files?" + urlencode({
            "q": "'" + route["drive_folder_id"].replace("'", "\\'") + "' in parents and trashed = false",
            "supportsAllDrives": "true", "includeItemsFromAllDrives": "true", "pageSize": 10,
            "fields": "files(id,size,mimeType,capabilities(canDownload,canTrash)),nextPageToken",
        }), drive_token)
        blobs = [f for f in sample.get("files", []) if not f.get("mimeType", "").startswith("application/vnd.google-apps.")]
        report["routes"].append({
            "drive_folder_accessible": True,
            "frame_folder_accessible": True,
            "sampled_binary_files": len(blobs),
            "largest_sample_bytes": max((int(f.get("size", 0)) for f in blobs), default=0),
            "sample_download_allowed": all(f.get("capabilities", {}).get("canDownload") is True for f in blobs) if blobs else None,
            "sample_trash_allowed": all(f.get("capabilities", {}).get("canTrash") is True for f in blobs) if blobs else None,
            "more_files_exist": bool(sample.get("nextPageToken")),
        })
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args(argv)
    try:
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
        print(json.dumps(inspect(config, offline=args.offline), indent=2))
        return 0
    except (ValueError, OSError, RuntimeError) as error:
        print(json.dumps({"read_only": True, "error": str(error)}, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
