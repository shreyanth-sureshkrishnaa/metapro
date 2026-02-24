import re
import subprocess
import json
import os
import shutil
from datetime import datetime

# ─── ExifTool wrapper ─────────────────────────────────────────────────────────

def run_exiftool(args):
    """Run exiftool with given args, return parsed JSON list."""
    cmd = ["exiftool", "-json"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr.strip() or "exiftool failed")
    return json.loads(result.stdout) if result.stdout.strip() else []


# ─── GPS helpers ──────────────────────────────────────────────────────────────

def parse_gps_coordinate(value_str):
    """Convert ExifTool GPS string like '37 deg 23' 14.50\" N' to decimal degrees."""
    if not value_str:
        return None
    try:
        return float(value_str)
    except ValueError:
        pass
    pattern = r"(\d+)\s+deg\s+(\d+)'\s+([\d.]+)\"\s+([NSEW])"
    m = re.search(pattern, str(value_str))
    if m:
        d, mi, s, direction = m.groups()
        decimal = int(d) + int(mi) / 60 + float(s) / 3600
        if direction in ('S', 'W'):
            decimal = -decimal
        return decimal
    return None


def extract_gps(entry):
    """Return (lat, lon) from an ExifTool JSON entry, or None."""
    lat = parse_gps_coordinate(entry.get("GPSLatitude") or entry.get("GPS Latitude"))
    lon = parse_gps_coordinate(entry.get("GPSLongitude") or entry.get("GPS Longitude"))
    if lat is not None and lon is not None:
        return (lat, lon)
    return None


# ─── Timeline helpers ─────────────────────────────────────────────────────────

KNOWN_DATE_FIELDS = [
    "DateTimeOriginal", "CreateDate", "ModifyDate",
    "FileModifyDate", "FileAccessDate", "FileCreateDate",
]


def parse_exif_datetime(value_str):
    """Try to parse an ExifTool datetime string into a Python datetime."""
    if not value_str:
        return None
    for fmt in ("%Y:%m:%d %H:%M:%S", "%Y:%m:%d %H:%M:%S%z",
                "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            cleaned = str(value_str).split("+")[0].split("-")[0] if "+" in str(value_str) else str(value_str)
            # Handle timezone offset like +05:30
            base = str(value_str).split("+")[0].split("Z")[0]
            return datetime.strptime(base.strip(), fmt.split("%z")[0].strip())
        except (ValueError, IndexError):
            continue
    return None


def get_best_datetime(entry):
    """Return the best datetime from an entry, preferring DateTimeOriginal."""
    for field in KNOWN_DATE_FIELDS:
        dt = parse_exif_datetime(entry.get(field))
        if dt:
            return dt
    return None


# ─── Anomaly detection ────────────────────────────────────────────────────────

EDITING_SOFTWARE = [
    "photoshop", "gimp", "lightroom", "snapseed", "pixlr",
    "affinity", "darktable", "rawtherapee", "capture one",
    "luminar", "paint.net", "paintshop", "acdsee",
    "faceapp", "facetune", "remini", "canva",
]


def detect_anomalies(entry):
    """Return a list of anomaly strings for a given metadata entry."""
    flags = []

    # 1. Future date
    dt = get_best_datetime(entry)
    if dt and dt > datetime.now():
        flags.append("FUTURE DATE: Creation date is in the future")

    # 2. Editing software detected
    software = str(entry.get("Software", "") or entry.get("CreatorTool", "") or "").lower()
    history_sw = str(entry.get("HistorySoftwareAgent", "")).lower()
    for editor in EDITING_SOFTWARE:
        if editor in software or editor in history_sw:
            flags.append(f"EDITED: Software field indicates editing ({entry.get('Software', entry.get('CreatorTool', 'Unknown'))})")
            break

    # 3. Missing GPS on a device that likely supports it
    has_gps = extract_gps(entry) is not None
    model = str(entry.get("Model", "")).lower()
    is_phone = any(kw in model for kw in ["iphone", "pixel", "galaxy", "oneplus", "xiaomi", "huawei", "samsung", "oppo", "vivo", "nothing", "motorola", "nokia", "lg"])
    if is_phone and not has_gps:
        flags.append("NO GPS: Smartphone photo missing GPS data (possibly stripped)")

    # 4. Mismatched file extension vs MIME type
    source = entry.get("SourceFile", "")
    mime = str(entry.get("MIMEType", "")).lower()
    ext = os.path.splitext(source)[1].lower()
    ext_mime_map = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".gif": "image/gif",
        ".tiff": "image/tiff", ".tif": "image/tiff",
        ".webp": "image/webp", ".bmp": "image/bmp",
        ".heic": "image/heic", ".heif": "image/heif",
    }
    if ext in ext_mime_map and mime and ext_mime_map[ext] != mime:
        flags.append(f"MIME MISMATCH: Extension {ext} but MIME is {mime}")

    # 5. Thumbnail present but different dimensions (possible crop/edit indicator)
    thumb_w = entry.get("ThumbnailImageWidth") or entry.get("ThumbnailWidth")
    thumb_h = entry.get("ThumbnailImageHeight") or entry.get("ThumbnailHeight")
    img_w = entry.get("ImageWidth") or entry.get("ExifImageWidth")
    img_h = entry.get("ImageHeight") or entry.get("ExifImageHeight")
    if all([thumb_w, thumb_h, img_w, img_h]):
        try:
            thumb_ratio = int(thumb_w) / max(int(thumb_h), 1)
            img_ratio = int(img_w) / max(int(img_h), 1)
            if abs(thumb_ratio - img_ratio) > 0.15:
                flags.append("ASPECT RATIO: Thumbnail aspect ratio differs from image (possible crop)")
        except (ValueError, ZeroDivisionError):
            pass

    return flags


# ─── Metadata stripping ──────────────────────────────────────────────────────

def strip_metadata(source_paths, output_dir):
    """
    Copy files to output_dir with all metadata stripped.
    Returns (success_count, error_list).
    """
    os.makedirs(output_dir, exist_ok=True)
    success = 0
    errors = []
    for src in source_paths:
        basename = os.path.basename(src)
        dest = os.path.join(output_dir, basename)
        # Handle duplicates
        counter = 1
        name, ext = os.path.splitext(basename)
        while os.path.exists(dest):
            dest = os.path.join(output_dir, f"{name}_{counter}{ext}")
            counter += 1
        try:
            shutil.copy2(src, dest)
            subprocess.run(["exiftool", "-all=", "-overwrite_original", dest],
                           capture_output=True, check=True)
            success += 1
        except Exception as e:
            errors.append(f"{basename}: {e}")
    return success, errors


# ─── Device fingerprinting ───────────────────────────────────────────────────

def get_device_summary(data_cache):
    """
    Return a list of dicts: [{device, software, count, files}]
    grouped by (Make + Model, Software).
    """
    devices = {}
    for entry in data_cache:
        make = str(entry.get("Make", "")).strip()
        model = str(entry.get("Model", "")).strip()
        software = str(entry.get("Software", entry.get("CreatorTool", ""))).strip()
        device = f"{make} {model}".strip() or "Unknown Device"
        key = (device, software or "N/A")
        if key not in devices:
            devices[key] = {"device": key[0], "software": key[1], "count": 0, "files": []}
        devices[key]["count"] += 1
        fname = os.path.basename(entry.get("SourceFile", "Unknown"))
        if len(devices[key]["files"]) < 5:
            devices[key]["files"].append(fname)
    return sorted(devices.values(), key=lambda x: x["count"], reverse=True)


# ─── HTML Report Generation ──────────────────────────────────────────────────

def generate_html_report(data_cache, output_path, case_info=None):
    """Generate a self-contained HTML forensic report."""
    case_info = case_info or {}
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    investigator = case_info.get("investigator", "N/A")
    case_name = case_info.get("case_name", "Metadata Analysis Report")
    notes = case_info.get("notes", "")

    # Gather data
    device_summary = get_device_summary(data_cache)
    timeline_entries = []
    all_anomalies = []
    gps_points = []

    for entry in data_cache:
        fname = os.path.basename(entry.get("SourceFile", "Unknown"))
        dt = get_best_datetime(entry)
        device = f"{entry.get('Make', '')} {entry.get('Model', '')}".strip() or "Unknown"
        coords = extract_gps(entry)
        anomalies = detect_anomalies(entry)

        timeline_entries.append({
            "file": fname,
            "datetime": dt.strftime("%Y-%m-%d %H:%M:%S") if dt else "N/A",
            "dt_sort": dt or datetime.min,
            "device": device,
            "gps": f"{coords[0]:.5f}, {coords[1]:.5f}" if coords else "N/A",
            "anomalies": anomalies,
        })

        if anomalies:
            all_anomalies.append({"file": fname, "flags": anomalies})

        if coords:
            gps_points.append({"lat": coords[0], "lon": coords[1], "label": fname})

    timeline_entries.sort(key=lambda x: x["dt_sort"])

    # Build HTML
    timeline_rows = ""
    for t in timeline_entries:
        anom_html = ""
        if t["anomalies"]:
            anom_html = '<br>'.join(f'<span class="flag">{a}</span>' for a in t["anomalies"])
        timeline_rows += f"""
        <tr>
            <td>{t['file']}</td>
            <td>{t['datetime']}</td>
            <td>{t['device']}</td>
            <td>{t['gps']}</td>
            <td>{anom_html or '<span class="clean">Clean</span>'}</td>
        </tr>"""

    device_rows = ""
    for d in device_summary:
        files_str = ", ".join(d["files"])
        if d["count"] > len(d["files"]):
            files_str += f" (+{d['count'] - len(d['files'])} more)"
        device_rows += f"""
        <tr>
            <td>{d['device']}</td>
            <td>{d['software']}</td>
            <td>{d['count']}</td>
            <td class="files-cell">{files_str}</td>
        </tr>"""

    anomaly_rows = ""
    for a in all_anomalies:
        for flag in a["flags"]:
            anomaly_rows += f"""
        <tr>
            <td>{a['file']}</td>
            <td><span class="flag">{flag}</span></td>
        </tr>"""

    map_html = ""
    if gps_points:
        avg_lat = sum(p["lat"] for p in gps_points) / len(gps_points)
        avg_lon = sum(p["lon"] for p in gps_points) / len(gps_points)
        zoom = 14 if len(gps_points) == 1 else 6
        pins_js = json.dumps(gps_points)
        map_html = f"""
        <h2>Geographic Distribution</h2>
        <div id="map" style="height:400px;border-radius:8px;border:1px solid #30363d;margin-bottom:24px;"></div>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script>
        var map = L.map('map').setView([{avg_lat}, {avg_lon}], {zoom});
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; OpenStreetMap'
        }}).addTo(map);
        var pins = {pins_js};
        pins.forEach(function(p) {{
            L.marker([p.lat, p.lon]).bindPopup('<b>' + p.label + '</b>').addTo(map);
        }});
        </script>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>{case_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
            background: #0d1117; color: #e6edf3;
            line-height: 1.6; padding: 40px;
        }}
        .report-header {{
            border-bottom: 2px solid #58a6ff;
            padding-bottom: 20px; margin-bottom: 32px;
        }}
        .report-header h1 {{
            font-size: 28px; font-weight: 700;
            color: #58a6ff; margin-bottom: 8px;
        }}
        .meta-info {{ color: #8b949e; font-size: 13px; }}
        .meta-info span {{ color: #e6edf3; font-weight: 500; }}
        h2 {{
            font-size: 18px; font-weight: 600;
            color: #58a6ff; margin: 24px 0 12px 0;
            border-left: 3px solid #58a6ff;
            padding-left: 12px;
        }}
        .summary-grid {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px; margin-bottom: 24px;
        }}
        .summary-card {{
            background: #161b22; border: 1px solid #30363d;
            border-radius: 8px; padding: 16px;
        }}
        .summary-card .label {{ color: #8b949e; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .summary-card .value {{ font-size: 24px; font-weight: 700; color: #e6edf3; margin-top: 4px; }}
        table {{
            width: 100%; border-collapse: collapse;
            background: #161b22; border: 1px solid #30363d;
            border-radius: 8px; overflow: hidden;
            margin-bottom: 24px;
        }}
        th {{
            background: #21262d; color: #8b949e;
            font-size: 11px; text-transform: uppercase;
            letter-spacing: 0.5px; text-align: left;
            padding: 10px 12px; border-bottom: 1px solid #30363d;
        }}
        td {{
            padding: 8px 12px; border-bottom: 1px solid #21262d;
            font-size: 13px;
        }}
        tr:hover td {{ background: #1c2129; }}
        .flag {{
            background: #3d1f1f; color: #f85149;
            padding: 2px 8px; border-radius: 4px;
            font-size: 11px; font-weight: 500;
            display: inline-block; margin: 1px 0;
        }}
        .clean {{
            background: #1a4a2e; color: #3fb950;
            padding: 2px 8px; border-radius: 4px;
            font-size: 11px; font-weight: 500;
        }}
        .files-cell {{ color: #8b949e; font-size: 12px; }}
        .footer {{
            margin-top: 40px; padding-top: 16px;
            border-top: 1px solid #30363d;
            color: #8b949e; font-size: 11px; text-align: center;
        }}
        .notes-box {{
            background: #161b22; border: 1px solid #30363d;
            border-radius: 8px; padding: 16px;
            color: #e6edf3; font-size: 13px;
            margin-bottom: 24px; white-space: pre-wrap;
        }}
    </style>
</head>
<body>
    <div class="report-header">
        <h1>{case_name}</h1>
        <div class="meta-info">
            Investigator: <span>{investigator}</span> &nbsp;|&nbsp;
            Generated: <span>{now}</span> &nbsp;|&nbsp;
            Files Analyzed: <span>{len(data_cache)}</span>
        </div>
    </div>

    {"<h2>Case Notes</h2><div class='notes-box'>" + notes + "</div>" if notes else ""}

    <h2>Summary</h2>
    <div class="summary-grid">
        <div class="summary-card">
            <div class="label">Total Files</div>
            <div class="value">{len(data_cache)}</div>
        </div>
        <div class="summary-card">
            <div class="label">Unique Devices</div>
            <div class="value">{len(device_summary)}</div>
        </div>
        <div class="summary-card">
            <div class="label">GPS-Tagged</div>
            <div class="value">{len(gps_points)}</div>
        </div>
        <div class="summary-card">
            <div class="label">Anomalies</div>
            <div class="value" style="color: {'#f85149' if all_anomalies else '#3fb950'}">{sum(len(a['flags']) for a in all_anomalies)}</div>
        </div>
    </div>

    <h2>Timeline</h2>
    <table>
        <thead>
            <tr><th>File</th><th>Date / Time</th><th>Device</th><th>GPS</th><th>Flags</th></tr>
        </thead>
        <tbody>{timeline_rows}</tbody>
    </table>

    <h2>Device Attribution</h2>
    <table>
        <thead>
            <tr><th>Device</th><th>Software</th><th>Count</th><th>Sample Files</th></tr>
        </thead>
        <tbody>{device_rows}</tbody>
    </table>

    {"<h2>Anomaly Report</h2><table><thead><tr><th>File</th><th>Flag</th></tr></thead><tbody>" + anomaly_rows + "</tbody></table>" if anomaly_rows else ""}

    {map_html}

    <div class="footer">
        Generated by MetaPro Forensic Report Engine &mdash; {now}
    </div>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path
