#!/usr/bin/env python3
"""Bounded, restoration-first validator for RC-0002 on an authorized DUT."""

from __future__ import annotations

import argparse
import hashlib
import http.client
import importlib.util
import ipaddress
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any


MARKER = "rc0002=1"
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_PACK_BYTES = 512 * 1024
EXPECTED_SOURCE_SHA256 = "7a39e043df2f1cdb4a5c677e496833f6b4048eab23538b457c416fb5da8b1461"


def require_private_target(target: str, allowed_cidr: str) -> str:
    address = ipaddress.ip_address(target)
    network = ipaddress.ip_network(allowed_cidr, strict=True)
    if (
        not address.is_private
        or address.is_loopback
        or address.is_link_local
        or address not in network
    ):
        raise ValueError("target must be a non-loopback private IP inside allowed CIDR")
    return str(address)


def require_verified_source(path: Path) -> tuple[Path, str]:
    source = path.resolve(strict=True)
    if not source.is_file() or source.stat().st_size > MAX_PACK_BYTES:
        raise ValueError("source pack is not a bounded regular file")
    digest = sha256(source)
    if digest != EXPECTED_SOURCE_SHA256:
        raise ValueError("source pack does not match the verified original RC-0002 language pack")
    return source, digest


def load_builder(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("rc0002_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load the marker builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def multipart_body(pack: bytes) -> tuple[bytes, str]:
    boundary = f"----rc0002-{uuid.uuid4().hex}"
    chunks = [
        f'--{boundary}\r\nContent-Disposition: form-data; name="ACTION"\r\n\r\nlangupdate\r\n'.encode(),
        (
            f'--{boundary}\r\nContent-Disposition: form-data; name="sealpac"; '
            'filename="sealpac.slp"\r\nContent-Type: application/octet-stream\r\n\r\n'
        ).encode(),
        pack,
        f"\r\n--{boundary}--\r\n".encode(),
    ]
    return b"".join(chunks), boundary


def request(
    target: str, method: str, path: str, body: bytes | None = None, content_type: str | None = None
) -> tuple[int, bytes]:
    connection = http.client.HTTPConnection(target, 80, timeout=10)
    headers = {"Connection": "close", "User-Agent": "rc0002-safe-validator/1"}
    if content_type:
        headers["Content-Type"] = content_type
    connection.request(method, path, body=body, headers=headers)
    response = connection.getresponse()
    payload = response.read(MAX_RESPONSE_BYTES + 1)
    connection.close()
    if len(payload) > MAX_RESPONSE_BYTES:
        raise RuntimeError("response exceeded the configured size limit")
    return response.status, payload


def upload(target: str, pack_path: Path) -> tuple[int, bytes]:
    pack = pack_path.read_bytes()
    if len(pack) > MAX_PACK_BYTES:
        raise ValueError("language pack exceeds the validator size limit")
    body, boundary = multipart_body(pack)
    return request(
        target,
        "POST",
        "/tools_fw_rlt.php",
        body,
        f"multipart/form-data; boundary={boundary}",
    )


def chromium_dom(target: str, output: Path, timeout: int) -> bytes:
    profile = output.parent / "chromium-profile"
    command = [
        "chromium",
        "--headless=new",
        "--disable-gpu",
        "--disable-extensions",
        "--disable-background-networking",
        "--disable-component-update",
        "--disable-sync",
        "--no-first-run",
        f"--user-data-dir={profile}",
        "--dump-dom",
        f"http://{target}/",
    ]
    completed = subprocess.run(command, check=False, capture_output=True, timeout=timeout)
    output.write_bytes(completed.stdout)
    if completed.returncode != 0:
        raise RuntimeError(f"Chromium exited with status {completed.returncode}")
    return completed.stdout


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="192.168.0.1")
    parser.add_argument("--allowed-cidr", default="192.168.0.0/24")
    parser.add_argument("--source-pack", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--ack-owned-authorized", action="store_true", required=True)
    parser.add_argument("--chromium-timeout", type=int, default=20)
    args = parser.parse_args()

    target = require_private_target(args.target, args.allowed_cidr)
    source_pack, source_sha256 = require_verified_source(args.source_pack)
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=False)
    builder_path = Path(__file__).with_name("build_inert_sealpac_marker.py")
    builder = load_builder(builder_path)
    derived_pack = output_dir / "derived-inert-marker.slp"
    result_path = output_dir / "result.json"
    result: dict[str, Any] = {
        "schema_version": "1",
        "target": target,
        "authorization_acknowledged": True,
        "persistent_change_intended": False,
        "source_pack_sha256": source_sha256,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "restoration": {"attempted": False, "verified": False},
    }

    builder.build_marker(source_pack, derived_pack, builder.MARKERS["dom"])
    result["derived_pack_sha256"] = sha256(derived_pack)
    failure: BaseException | None = None
    try:
        before_status, before = request(target, "GET", "/")
        (output_dir / "before.body").write_bytes(before)
        if MARKER.encode() in before:
            raise RuntimeError("marker was already present before validation")
        upload_status, upload_body = upload(target, derived_pack)
        (output_dir / "upload.body").write_bytes(upload_body)
        after_status, after = request(target, "GET", "/")
        (output_dir / "after.body").write_bytes(after)
        dom = chromium_dom(target, output_dir / "headless-dom.body", args.chromium_timeout)
        result["validation"] = {
            "before_http_status": before_status,
            "upload_http_status": upload_status,
            "after_http_status": after_status,
            "marker_in_http_response": MARKER.encode() in after,
            "marker_executed_in_dom": b'data-rc0002="1"' in dom,
        }
        if not result["validation"]["marker_executed_in_dom"]:
            raise RuntimeError("the inert DOM marker was not observed")
    except BaseException as exc:
        failure = exc
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        result["restoration"]["attempted"] = True
        try:
            restore_status, restore_body = upload(target, source_pack)
            (output_dir / "restore.body").write_bytes(restore_body)
            final_status, final_body = request(target, "GET", "/")
            (output_dir / "final.body").write_bytes(final_body)
            restored = MARKER.encode() not in final_body and b'data-rc0002="1"' not in final_body
            result["restoration"].update(
                {
                    "upload_http_status": restore_status,
                    "final_http_status": final_status,
                    "verified": restored,
                }
            )
            if not restored and failure is None:
                failure = RuntimeError("restoration could not be verified")
        except BaseException as exc:
            result["restoration"]["error"] = f"{type(exc).__name__}: {exc}"
            if failure is None:
                failure = exc

    result["completed_at"] = datetime.now(timezone.utc).isoformat()
    result["artifacts"] = {
        path.name: sha256(path)
        for path in sorted(output_dir.iterdir())
        if path.is_file() and path != result_path
    }
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failure is not None:
        print(f"validation failed: {failure}", file=sys.stderr)
        return 1
    print(result_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
