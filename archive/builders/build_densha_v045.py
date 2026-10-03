#!/usr/bin/env python3
"""Build Densha de Go! 2 (WonderSwan) English v0.4.5.

Incremental base: EN v0.4.4.
This release repairs the persistent gameplay HUD labels identified by runtime
screenshots and a Work RAM/tilemap trace:

  次駅   -> NEXT
  現在   -> NOW
  非常   -> EMG
  通過駅 -> PASS STN

The original game reuses tile 40 (駅) in both 次駅 and 通過駅.  To avoid a
shared-tile collision, the code that writes the final tile of 通過駅 is patched
to use spare tile 47 instead.  Tile 47 had already been overwritten by an
older incomplete PASS patch but was not referenced by the captured gameplay
BG/OAM state, so this change makes that allocation explicit and deterministic.
"""
from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
import csv
import hashlib
import json
import shutil
import zipfile

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path('/mnt/data')
BASE = ROOT / 'Densha_de_Go_2_EN_v0.4.4.ws'
ORIG = ROOT / 'Densha de Go! 2 (Japan).ws'
OUT = ROOT / 'Densha_de_Go_2_EN_v0.4.5.ws'
IPS = ROOT / 'Densha_de_Go_2_EN_v0.4.5.ips'
WORK = ROOT / 'densha_v045_work'
PREV = WORK / 'previews'
REPORTS = WORK / 'reports'
RUNTIME = WORK / 'runtime'
PACKAGE_DIR = ROOT / 'Densha_de_Go_2_EN_v0.4.5_package'
PACKAGE_ZIP = ROOT / 'Densha_de_Go_2_EN_v0.4.5_package.zip'

HUD_OFFSET = 0x3D6609
HUD_EXPECTED_OUT = 1024
HUD_ORIGINAL_CAPACITY = 766
TILEMAP_CODE_PATTERN = bytes.fromhex(
    'BB3014C7071C04C747021D04C747041E04C747062804'
)
TILEMAP_CODE_REPLACEMENT = bytes.fromhex(
    'BB3014C7071C04C747021D04C747041E04C747062F04'
)

for p in (WORK, PREV, REPORTS, RUNTIME):
    p.mkdir(parents=True, exist_ok=True)

FONT3 = {
    'A':["010","101","111","101","101"], 'B':["110","101","110","101","110"],
    'C':["011","100","100","100","011"], 'D':["110","101","101","101","110"],
    'E':["111","100","110","100","111"], 'F':["111","100","110","100","100"],
    'G':["011","100","101","101","011"], 'H':["101","101","111","101","101"],
    'I':["111","010","010","010","111"], 'J':["001","001","001","101","010"],
    'K':["101","101","110","101","101"], 'L':["100","100","100","100","111"],
    'M':["101","111","111","101","101"], 'N':["101","111","111","111","101"],
    'O':["111","101","101","101","111"], 'P':["110","101","110","100","100"],
    'Q':["111","101","101","111","001"], 'R':["110","101","110","101","101"],
    'S':["011","100","111","001","110"], 'T':["111","010","010","010","010"],
    'U':["101","101","101","101","111"], 'V':["101","101","101","101","010"],
    'W':["101","101","111","111","101"], 'X':["101","101","010","101","101"],
    'Y':["101","101","010","010","010"], 'Z':["111","001","010","100","111"],
    '0':["111","101","101","101","111"], '1':["010","110","010","010","111"],
    '2':["110","001","010","100","111"], '3':["110","001","010","001","110"],
    '4':["101","101","111","001","001"], '5':["111","100","110","001","110"],
    '6':["011","100","111","101","111"], '7':["111","001","010","010","010"],
    '8':["111","101","111","101","111"], '9':["111","101","111","001","110"],
    '.':["000","000","000","000","010"], '-':["000","000","111","000","000"],
    ' ':["000","000","000","000","000"],
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def dec_stream(data: bytes | bytearray, off: int) -> tuple[bytes, int]:
    if off < 0 or off + 2 > len(data):
        raise ValueError(f'Invalid stream offset: 0x{off:X}')
    n = data[off] | (data[off + 1] << 8)
    p = off + 2
    out = bytearray()
    while len(out) < n:
        if p >= len(data):
            raise ValueError('Unexpected EOF while reading flags')
        flags = data[p]
        p += 1
        for _ in range(8):
            if len(out) >= n:
                break
            if flags & 1:
                if p >= len(data):
                    raise ValueError('Unexpected EOF while reading literal')
                out.append(data[p])
                p += 1
            else:
                if p + 1 >= len(data):
                    raise ValueError('Unexpected EOF while reading reference')
                word = data[p] | (data[p + 1] << 8)
                p += 2
                length = (word & 0x0F) + 3
                distance = word >> 4
                src = len(out) - distance
                for _ in range(length):
                    if len(out) >= n:
                        break
                    if src < 0 or src >= len(out):
                        out.append(0)
                    else:
                        out.append(out[src])
                    src += 1
            flags >>= 1
    return bytes(out), p - off


def compress_ws(data: bytes) -> bytes:
    n = len(data)
    pos = 0
    tokens: list[tuple] = []
    history: dict[bytes, deque[int]] = defaultdict(deque)

    def add(p: int) -> None:
        if p + 3 <= n:
            history[data[p:p + 3]].append(p)

    while pos < n:
        max_len = min(18, n - pos)
        best_len = 0
        best_dist = 0

        # The game decoder permits a pre-buffer zero reference.  This is very
        # effective for blank tile regions and matches previous project builds.
        if data[pos] == 0:
            z = 0
            while z < max_len and data[pos + z] == 0:
                z += 1
            if z >= 3 and pos + z <= 4095:
                best_len = z
                best_dist = pos + z

        if pos + 3 <= n:
            dq = history.get(data[pos:pos + 3])
            if dq:
                while dq and pos - dq[0] > 4095:
                    dq.popleft()
                for src in reversed(dq):
                    distance = pos - src
                    length = 3
                    while length < max_len and data[pos + length] == data[src + length]:
                        length += 1
                    if length > best_len:
                        best_len = length
                        best_dist = distance
                        if length == max_len:
                            break

        if best_len >= 3:
            tokens.append(('r', best_dist, best_len))
            old = pos
            pos += best_len
            for p in range(old, pos):
                add(p)
        else:
            tokens.append(('l', data[pos]))
            add(pos)
            pos += 1

    out = bytearray([n & 0xFF, (n >> 8) & 0xFF])
    for i in range(0, len(tokens), 8):
        group = tokens[i:i + 8]
        flags = 0
        payload = bytearray()
        for bit, token in enumerate(group):
            if token[0] == 'l':
                flags |= 1 << bit
                payload.append(token[1])
            else:
                _, distance, length = token
                word = (distance << 4) | (length - 3)
                payload += bytes([word & 0xFF, word >> 8])
        out.append(flags)
        out += payload
    return bytes(out)


def tiles_arrays(data: bytes) -> list[np.ndarray]:
    if len(data) % 16:
        raise ValueError('Tile data length is not a multiple of 16')
    arrs: list[np.ndarray] = []
    for tile_index in range(len(data) // 16):
        tile = data[tile_index * 16:(tile_index + 1) * 16]
        arr = np.zeros((8, 8), dtype=np.uint8)
        for y in range(8):
            p0, p1 = tile[y * 2], tile[y * 2 + 1]
            for x in range(8):
                bit = 7 - x
                arr[y, x] = ((p0 >> bit) & 1) | (((p1 >> bit) & 1) << 1)
        arrs.append(arr)
    return arrs


def arrays_to_data(arrs: list[np.ndarray]) -> bytes:
    out = bytearray()
    for arr in arrs:
        if arr.shape != (8, 8):
            raise ValueError(f'Unexpected tile shape: {arr.shape}')
        for y in range(8):
            p0 = 0
            p1 = 0
            for x in range(8):
                value = int(arr[y, x])
                bit = 7 - x
                p0 |= (value & 1) << bit
                p1 |= ((value >> 1) & 1) << bit
            out += bytes([p0, p1])
    return bytes(out)


def text_width(text: str, spacing: int = 1) -> int:
    if not text:
        return 0
    return sum(len(FONT3.get(ch, FONT3[' '])[0]) for ch in text) + spacing * (len(text) - 1)


def patch_tiles(
    raw: bytes,
    indices: list[int],
    text: str,
    *,
    background: int,
    foreground: int = 3,
    spacing: int = 1,
    y: int = 1,
) -> tuple[bytes, np.ndarray]:
    arrs = tiles_arrays(raw)
    width = len(indices) * 8
    canvas = np.full((8, width), background, dtype=np.uint8)
    tw = text_width(text, spacing)
    if tw > width:
        raise ValueError(f'{text!r} needs {tw}px, only {width}px available')
    x = (width - tw) // 2
    cursor = x
    for ch in text:
        glyph = FONT3.get(ch, FONT3[' '])
        glyph_width = len(glyph[0])
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == '1':
                    px = cursor + gx
                    py = y + gy
                    if 0 <= px < width and 0 <= py < 8:
                        canvas[py, px] = foreground
        cursor += glyph_width + spacing
    for column, tile_id in enumerate(indices):
        arrs[tile_id] = canvas[:, column * 8:(column + 1) * 8].copy()
    return arrays_to_data(arrs), canvas


def render_resource(raw: bytes, path: Path, *, columns: int = 32, scale: int = 5, labels: bool = True) -> None:
    arrs = tiles_arrays(raw)
    rows = (len(arrs) + columns - 1) // columns
    label_h = 8 if labels else 0
    img = Image.new('L', (columns * 8, rows * (8 + label_h)), 255)
    draw = ImageDraw.Draw(img)
    palette = np.array([255, 170, 85, 0], dtype=np.uint8)
    for i, arr in enumerate(arrs):
        x = (i % columns) * 8
        y = (i // columns) * (8 + label_h)
        img.paste(Image.fromarray(palette[arr], mode='L'), (x, y))
        if labels:
            draw.text((x, y + 8), str(i), fill=0)
    if scale != 1:
        img = img.resize((img.width * scale, img.height * scale), Image.Resampling.NEAREST)
    img.save(path)


def save_comparison(before: dict[str, np.ndarray], after: dict[str, np.ndarray], path: Path) -> None:
    labels = ['NEXT', 'NOW', 'EMG', 'PASS STN']
    row_h = 58
    width = 760
    image = Image.new('RGB', (width, row_h * len(labels) + 32), 'white')
    draw = ImageDraw.Draw(image)
    draw.text((8, 5), 'Japanese/original resource', fill='black')
    draw.text((385, 5), 'English v0.4.5', fill='black')
    lut = np.array([255, 170, 85, 0], dtype=np.uint8)
    for row, label in enumerate(labels):
        y = 30 + row * row_h
        draw.text((8, y + 10), label, fill='black')
        for x0, source in ((120, before[label]), (495, after[label])):
            tile_img = Image.fromarray(lut[source], mode='L').resize(
                (source.shape[1] * 4, source.shape[0] * 4), Image.Resampling.NEAREST
            ).convert('RGB')
            image.paste(tile_img, (x0, y))
    image.save(path)


def ips_create(src: bytes, dst: bytes) -> bytes:
    if len(src) != len(dst):
        raise ValueError('This simple IPS builder requires equal-sized files')
    out = bytearray(b'PATCH')
    i = 0
    while i < len(src):
        if src[i] == dst[i]:
            i += 1
            continue
        start = i
        chunk = bytearray()
        while i < len(src) and src[i] != dst[i] and len(chunk) < 0xFFFF:
            chunk.append(dst[i])
            i += 1
        out += start.to_bytes(3, 'big')
        out += len(chunk).to_bytes(2, 'big')
        out += chunk
    out += b'EOF'
    return bytes(out)


def ips_apply(src: bytes, patch: bytes) -> bytes:
    if not patch.startswith(b'PATCH'):
        raise ValueError('Invalid IPS header')
    out = bytearray(src)
    p = 5
    while patch[p:p + 3] != b'EOF':
        off = int.from_bytes(patch[p:p + 3], 'big')
        p += 3
        size = int.from_bytes(patch[p:p + 2], 'big')
        p += 2
        if size == 0:
            rle_len = int.from_bytes(patch[p:p + 2], 'big')
            value = patch[p + 2]
            p += 3
            out[off:off + rle_len] = bytes([value]) * rle_len
        else:
            out[off:off + size] = patch[p:p + size]
            p += size
    return bytes(out)


def extract_canvas(raw: bytes, ids: list[int]) -> np.ndarray:
    arrs = tiles_arrays(raw)
    return np.concatenate([arrs[i] for i in ids], axis=1)


def main() -> None:
    for required in (BASE, ORIG):
        if not required.is_file():
            raise FileNotFoundError(required)

    base_bytes = BASE.read_bytes()
    original_bytes = ORIG.read_bytes()
    if len(base_bytes) != 4 * 1024 * 1024 or len(original_bytes) != 4 * 1024 * 1024:
        raise RuntimeError('Unexpected ROM size; expected exactly 4 MiB')

    rom = bytearray(base_bytes)
    pristine_hud, pristine_len = dec_stream(original_bytes, HUD_OFFSET)
    base_hud, base_len = dec_stream(base_bytes, HUD_OFFSET)
    if len(pristine_hud) != HUD_EXPECTED_OUT or len(base_hud) != HUD_EXPECTED_OUT:
        raise RuntimeError('Unexpected HUD decompressed size')
    if pristine_len != HUD_ORIGINAL_CAPACITY:
        raise RuntimeError(f'Unexpected pristine HUD capacity: {pristine_len}')

    before = {
        'NEXT': extract_canvas(pristine_hud, [39, 40]),
        'NOW': extract_canvas(pristine_hud, [41, 42]),
        'EMG': extract_canvas(pristine_hud, [26, 27]),
        'PASS STN': extract_canvas(pristine_hud, [28, 29, 30, 40]),
    }

    # Start from the current translated bank to preserve unrelated v0.4.4 HUD work,
    # but explicitly normalize the backgrounds of the four repaired labels.
    hud = base_hud
    manifest: list[dict[str, object]] = []

    patches = [
        ('Emergency brake', [26, 27], 'EMG', 2),
        ('Passing-station label', [28, 29, 30, 47], 'PASS STN', 0),
        ('Next-station label', [39, 40], 'NEXT', 0),
        ('Current-time label', [41, 42], 'NOW', 0),
    ]
    after_canvases: dict[str, np.ndarray] = {}
    for label, ids, text, background in patches:
        hud, canvas = patch_tiles(
            hud, ids, text, background=background, foreground=3, spacing=1, y=1
        )
        after_canvases[text] = canvas
        manifest.append({
            'type': 'tile_graphics',
            'label': label,
            'rom_offset': f'0x{HUD_OFFSET:06X}',
            'tile_ids': ' '.join(str(i) for i in ids),
            'english': text,
            'background_index': background,
        })

    compressed = compress_ws(hud)
    if len(compressed) > HUD_ORIGINAL_CAPACITY:
        raise RuntimeError(
            f'HUD compressed size {len(compressed)} exceeds {HUD_ORIGINAL_CAPACITY}'
        )
    roundtrip, consumed = dec_stream(compressed, 0)
    if roundtrip != hud or consumed != len(compressed):
        raise RuntimeError('HUD codec round-trip failed')
    rom[HUD_OFFSET:HUD_OFFSET + len(compressed)] = compressed

    # The bottom-right label used tile 40 (shared with NEXT). Redirect just that
    # final tile to spare tile 47.  Assert unique pattern to avoid blind patching.
    hits: list[int] = []
    start = 0
    while True:
        hit = bytes(rom).find(TILEMAP_CODE_PATTERN, start)
        if hit < 0:
            break
        hits.append(hit)
        start = hit + 1
    if hits != [0x3F7C90]:
        raise RuntimeError(f'Unexpected tilemap code pattern locations: {hits}')
    code_off = hits[0]
    rom[code_off:code_off + len(TILEMAP_CODE_REPLACEMENT)] = TILEMAP_CODE_REPLACEMENT
    manifest.append({
        'type': 'code_immediate',
        'label': 'Separate PASS STN final tile from shared NEXT tile',
        'rom_offset': '0x3F7CA4',
        'tile_ids': '40 -> 47',
        'english': 'PASS STN',
        'background_index': '',
    })

    # Recalculate WonderSwan checksum (little-endian sum of every preceding byte).
    rom[-2:] = b'\x00\x00'
    checksum = sum(rom[:-2]) & 0xFFFF
    rom[-2] = checksum & 0xFF
    rom[-1] = checksum >> 8

    out_bytes = bytes(rom)
    OUT.write_bytes(out_bytes)
    ips = ips_create(original_bytes, out_bytes)
    IPS.write_bytes(ips)

    # Binary validations.
    rebuilt_hud, rebuilt_len = dec_stream(out_bytes, HUD_OFFSET)
    if rebuilt_hud != hud:
        raise RuntimeError('Patched ROM HUD does not decompress to expected bytes')
    if rebuilt_len != len(compressed):
        raise RuntimeError('Patched ROM HUD compressed length mismatch')
    if ips_apply(original_bytes, ips) != out_bytes:
        raise RuntimeError('IPS reapplication does not reproduce the output ROM')
    if out_bytes[0x3F7CA4:0x3F7CA6] != bytes.fromhex('2F04'):
        raise RuntimeError('Tilemap immediate patch is missing')
    stored_checksum = out_bytes[-2] | (out_bytes[-1] << 8)
    calculated_checksum = sum(out_bytes[:-2]) & 0xFFFF
    if stored_checksum != calculated_checksum:
        raise RuntimeError('WonderSwan checksum mismatch')

    # Scope check: expected changes are HUD allocation, one code byte, checksum.
    diff_indices = [i for i, (a, b) in enumerate(zip(base_bytes, out_bytes)) if a != b]
    allowed = set(range(HUD_OFFSET, HUD_OFFSET + HUD_ORIGINAL_CAPACITY))
    allowed.add(0x3F7CA4)
    allowed.update((len(out_bytes) - 2, len(out_bytes) - 1))
    unexpected = [i for i in diff_indices if i not in allowed]
    if unexpected:
        raise RuntimeError(f'Unexpected byte changes outside allowed regions: {unexpected[:16]}')

    render_resource(pristine_hud, PREV / 'hud_pristine_tiles.png')
    render_resource(base_hud, PREV / 'hud_v044_tiles.png')
    render_resource(hud, PREV / 'hud_v045_tiles.png')
    save_comparison(before, {
        'NEXT': after_canvases['NEXT'],
        'NOW': after_canvases['NOW'],
        'EMG': after_canvases['EMG'],
        'PASS STN': after_canvases['PASS STN'],
    }, PREV / 'hud_labels_before_after.png')

    manifest_path = WORK / 'v045_patch_manifest.csv'
    with manifest_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'type', 'label', 'rom_offset', 'tile_ids', 'english', 'background_index'
        ])
        writer.writeheader()
        writer.writerows(manifest)

    validation = {
        'version': '0.4.5',
        'base': {
            'path': str(BASE),
            'size': len(base_bytes),
            'sha256': sha256(base_bytes),
        },
        'output': {
            'path': str(OUT),
            'size': len(out_bytes),
            'sha256': sha256(out_bytes),
            'ws_checksum_stored': f'0x{stored_checksum:04X}',
            'ws_checksum_calculated': f'0x{calculated_checksum:04X}',
        },
        'ips': {
            'path': str(IPS),
            'size': len(ips),
            'sha256': sha256(ips),
            'reapplication_exact': True,
        },
        'hud_resource': {
            'offset': f'0x{HUD_OFFSET:06X}',
            'decompressed_size': len(hud),
            'base_compressed_size': base_len,
            'allocation_capacity': HUD_ORIGINAL_CAPACITY,
            'new_compressed_size': len(compressed),
            'free_bytes': HUD_ORIGINAL_CAPACITY - len(compressed),
            'codec_roundtrip_exact': True,
        },
        'tilemap_code': {
            'pattern_offset': '0x3F7C90',
            'immediate_offset': '0x3F7CA4',
            'old_word': '0x0428 (tile 40)',
            'new_word': '0x042F (tile 47)',
            'unique_pattern_asserted': True,
        },
        'translations': {
            '次駅': 'NEXT',
            '現在': 'NOW',
            '非常': 'EMG',
            '通過駅': 'PASS STN',
        },
        'diff_scope': {
            'changed_bytes_vs_v044': len(diff_indices),
            'unexpected_changes': 0,
        },
        'runtime_validation': 'pending',
    }
    (REPORTS / 'V045_BINARY_VALIDATION.json').write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )

    report_lines = [
        'DENSHA DE GO! 2 (WONDERSWAN) ENGLISH v0.4.5 BUILD',
        '',
        'HUD translations:',
        '  次駅   -> NEXT',
        '  現在   -> NOW',
        '  非常   -> EMG',
        '  通過駅 -> PASS STN',
        '',
        f'Base v0.4.4 SHA-256: {sha256(base_bytes)}',
        f'ROM v0.4.5 SHA-256:  {sha256(out_bytes)}',
        f'IPS SHA-256:         {sha256(ips)}',
        f'ROM size:            {len(out_bytes)} bytes',
        f'WonderSwan checksum:  0x{checksum:04X}',
        f'HUD compressed:       {len(compressed)} / {HUD_ORIGINAL_CAPACITY} bytes',
        f'HUD free space:       {HUD_ORIGINAL_CAPACITY - len(compressed)} bytes',
        f'Changed bytes vs base:{len(diff_indices)}',
        'Unexpected changes:    0',
        'IPS exact rebuild:     PASS',
        'Codec round-trip:      PASS',
        '',
        'Runtime validation must be performed after this build.',
    ]
    (WORK / 'V045_BUILD_REPORT.txt').write_text('\n'.join(report_lines) + '\n', encoding='utf-8')

    print('\n'.join(report_lines))


if __name__ == '__main__':
    main()
