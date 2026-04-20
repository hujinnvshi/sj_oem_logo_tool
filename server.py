#!/usr/bin/env python3
"""
Secsmart Reskin Tool - HTTP Server with OEM Archive API
Serves static files and provides /api/save endpoint for archiving oem.zip
"""

import os
import io
import re
import json
import zipfile
import hashlib
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote

WORKDIR = os.path.dirname(os.path.abspath(__file__))
OEM_DIR = os.path.join(WORKDIR, "OEM_ZIYUAN")


def sanitize_name(name):
    """Sanitize folder/filename: remove unsafe chars, strip spaces."""
    name = name.strip()
    name = re.sub(r'[\\/:*?"<>|]', '_', name)
    name = re.sub(r'\s+', '_', name)
    return name if name else "Unknown"


def file_hash(filepath):
    """Calculate MD5 hash of a file for dedup."""
    h = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


class OEMHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WORKDIR, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/library':
            self._handle_library()
        else:
            super().do_GET()

    def _handle_library(self):
        """Scan OEM_ZIYUAN/ and return vendor/product tree as JSON."""
        try:
            if not os.path.isdir(OEM_DIR):
                self._send_json(200, {"vendors": []})
                return

            vendors = []
            for vendor_name in sorted(os.listdir(OEM_DIR)):
                vendor_path = os.path.join(OEM_DIR, vendor_name)
                if not os.path.isdir(vendor_path):
                    continue

                products = []
                images = []
                for fname in sorted(os.listdir(vendor_path)):
                    fpath = os.path.join(vendor_path, fname)
                    if fname.endswith('_oeminfo.xlsx') and os.path.isfile(fpath):
                        product_name = fname.replace('_oeminfo.xlsx', '')
                        products.append({
                            "name": product_name,
                            "xlsxFile": quote(f"OEM_ZIYUAN/{vendor_name}/{fname}", safe='/')
                        })

                # Scan images/
                images_dir = os.path.join(vendor_path, "images")
                if os.path.isdir(images_dir):
                    for img_name in sorted(os.listdir(images_dir)):
                        img_path = os.path.join(images_dir, img_name)
                        if os.path.isfile(img_path):
                            images.append({
                                "name": img_name,
                                "url": quote(f"OEM_ZIYUAN/{vendor_name}/images/{img_name}", safe='/')
                            })

                vendors.append({
                    "name": vendor_name,
                    "products": products,
                    "images": images
                })

            self._send_json(200, {"vendors": vendors})
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/save':
            self._handle_save()
        elif parsed.path == '/api/save-preview':
            self._handle_save_preview()
        else:
            self._send_json(404, {"error": "Not found"})

    def _handle_save(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0 or content_length > 50 * 1024 * 1024:
                self._send_json(400, {"error": "Invalid content size"})
                return

            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))

            zip_b64 = data.get('zip')
            manufacturer = data.get('manufacturer', '').strip() or '白牌'
            product_name = data.get('productName', '').strip()

            if not zip_b64:
                self._send_json(400, {"error": "Missing zip data"})
                return

            # Decode base64 zip
            import base64
            zip_bytes = base64.b64decode(zip_b64)
            zf = zipfile.ZipFile(io.BytesIO(zip_bytes))

            # Determine vendor folder
            vendor_dir = os.path.join(OEM_DIR, sanitize_name(manufacturer))
            images_dir = os.path.join(vendor_dir, "images")
            os.makedirs(images_dir, exist_ok=True)

            saved_images = []
            skipped_images = []
            saved_config = None

            for entry in zf.namelist():
                basename = os.path.basename(entry)
                if not basename:
                    continue

                if entry.startswith('oem/images/'):
                    dest = os.path.join(images_dir, basename)
                    # Dedup: skip if identical file already exists
                    entry_bytes = zf.read(entry)
                    if os.path.exists(dest):
                        existing_hash = file_hash(dest)
                        new_hash = hashlib.md5(entry_bytes).hexdigest()
                        if existing_hash == new_hash:
                            skipped_images.append(basename)
                            continue
                    with open(dest, 'wb') as f:
                        f.write(entry_bytes)
                    saved_images.append(basename)

                elif entry.endswith('.xlsx'):
                    # Save as: 产品名称_oeminfo.xlsx
                    if product_name:
                        config_name = f"{sanitize_name(product_name)}_oeminfo.xlsx"
                    else:
                        config_name = "default_oeminfo.xlsx"
                    dest = os.path.join(vendor_dir, config_name)
                    with open(dest, 'wb') as f:
                        f.write(zf.read(entry))
                    saved_config = config_name

                elif entry.startswith('oem/files/'):
                    # License agreement files
                    files_dir = os.path.join(vendor_dir, "files")
                    os.makedirs(files_dir, exist_ok=True)
                    dest = os.path.join(files_dir, basename)
                    with open(dest, 'wb') as f:
                        f.write(zf.read(entry))

            result = {
                "success": True,
                "vendor": manufacturer,
                "vendorDir": vendor_dir,
                "savedImages": saved_images,
                "skippedImages": skipped_images,
                "savedConfig": saved_config,
            }
            self._send_json(200, result)

        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _handle_save_preview(self):
        """Save preview screenshot PNG to OEM_ZIYUAN/vendor/previews/"""
        try:
            import base64
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0 or content_length > 10 * 1024 * 1024:
                self._send_json(400, {"error": "Invalid content size"})
                return

            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))

            image_b64 = data.get('image')
            manufacturer = data.get('manufacturer', '').strip() or '白牌'
            filename = data.get('filename', 'preview.png')

            if not image_b64:
                self._send_json(400, {"error": "Missing image data"})
                return

            vendor_dir = os.path.join(OEM_DIR, sanitize_name(manufacturer))
            previews_dir = os.path.join(vendor_dir, "previews")
            os.makedirs(previews_dir, exist_ok=True)

            # Strip data URL prefix if present
            if ',' in image_b64:
                image_b64 = image_b64.split(',', 1)[1]

            image_bytes = base64.b64decode(image_b64)
            safe_filename = sanitize_name(filename)
            if not safe_filename.endswith('.png'):
                safe_filename += '.png'

            dest = os.path.join(previews_dir, safe_filename)
            with open(dest, 'wb') as f:
                f.write(image_bytes)

            self._send_json(200, {
                "success": True,
                "path": dest,
                "size": len(image_bytes),
            })

        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _send_json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(body))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        """Log to file instead of stderr."""
        log_path = os.path.join(WORKDIR, "server.log")
        timestamp = self.log_date_time_string()
        with open(log_path, 'a') as f:
            f.write(f"[{timestamp}] {format % args}\n")


if __name__ == '__main__':
    PORT = 47191
    server = HTTPServer(('0.0.0.0', PORT), OEMHandler)
    print(f"Server running on http://0.0.0.0:{PORT}")
    server.serve_forever()
