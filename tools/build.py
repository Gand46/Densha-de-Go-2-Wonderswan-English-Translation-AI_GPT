#!/usr/bin/env python3
"""Reproduce the test release, or build an explicitly marked development ROM."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
from codec import compress_ws, dec_stream

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'vendor'))
from ws_patch_tools import bps, ips


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def project_file(name):
    path = (ROOT / name).resolve()
    require(path.is_relative_to(ROOT), 'Resource paths must stay within the project')
    return path


def render_heading(raw, text, font):
    require(len(raw) == 1152, 'Unexpected heading atlas size')
    require(0 < len(text) * 6 - 1 <= 94, 'Heading exceeds its 96-pixel field')
    require(all(ch == ' ' or ch in font for ch in text), 'Unsupported heading character')
    pixels = [[0] * 96 for _ in range(16)]
    points = []
    x = (96 - (len(text) * 6 - 1)) // 2
    for char in text:
        if char != ' ':
            glyph = font[char]
            require(len(glyph) == 7 and all(len(row) == 5 and set(row) <= {'0', '1'} for row in glyph), 'Invalid 5x7 glyph')
            for y, row in enumerate(glyph):
                points.extend((x + dx, y + 4) for dx, bit in enumerate(row) if bit == '1')
        x += 6
    for x, y in points:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if 0 <= x + dx < 96 and 0 <= y + dy < 16:
                    pixels[y + dy][x + dx] = 2
    for x, y in points:
        pixels[y][x] = 1
    result = bytearray(raw)
    for tile in range(24):
        tx, ty = tile % 12 * 8, tile // 12 * 8
        packed = bytearray()
        for y in range(8):
            row = pixels[ty + y][tx:tx + 8]
            packed.extend([sum(bool(v & 1) << (7 - i) for i, v in enumerate(row)), sum(bool(v & 2) << (7 - i) for i, v in enumerate(row))])
        result[tile * 16:(tile + 1) * 16] = packed
    require(result[384:] == raw[384:], 'Non-heading tiles changed')
    return bytes(result)


def build(original, development=False):
    meta = load_json(ROOT / 'project.json')
    require(len(original) == meta['rom_bytes'] and sha(original) == meta['original_sha256'], 'Wrong original ROM: check project.json for size and SHA-256')
    baseline = ips.apply(original, project_file(meta['baseline_patch']).read_bytes())
    require(sha(baseline) == meta['baseline_sha256'], 'Baseline patch is damaged or incompatible')
    rom = bytearray(baseline)
    allowed, offsets, changes = set(), set(), []
    inventory = load_json(ROOT / 'translations/GLOBAL_RESOURCE_INVENTORY.json')['resources']
    valid_streams = {int(row['stream'], 16) for row in inventory if 'stream' in row}

    def replace_stream(offset, raw, reason):
        require(offset in valid_streams, 'Offset is not a known compressed resource')
        require(offset not in offsets, 'Duplicate resource override')
        offsets.add(offset)
        old, _ = dec_stream(original, offset)
        require(len(raw) == len(old), 'Resource length changed')
        require(original[offset - 2:offset] == b'\x00\xc0', 'Wrong compression descriptor')
        _, capacity = dec_stream(original, offset)
        packed = compress_ws(raw)
        require(len(packed) <= capacity, f'Resource at {offset:#x} exceeds original capacity')
        require(dec_stream(packed, 0) == (raw, len(packed)), 'Compression roundtrip failed')
        rom[offset:offset + len(packed)] = packed
        allowed.update(range(offset, offset + len(packed)))
        changes.append({'offset':hex(offset), 'raw_bytes':len(raw), 'packed_bytes':len(packed), 'capacity':capacity, 'reason':reason})

    font = load_json(ROOT / 'assets/font5x7.json')
    for record in load_json(project_file(meta['headings'])):
        offset = int(record['offset'], 0)
        raw, _ = dec_stream(baseline, offset)
        replace_stream(offset, render_heading(raw, record['text'], font), record['text'])
    overrides = load_json(project_file(meta['resource_overrides']))
    require(not overrides or development, 'Resource overrides require --development')
    for record in overrides:
        replace_stream(int(record['offset'], 0), project_file(record['file']).read_bytes(), record.get('reason', 'Development override'))
    rom[-2:] = (sum(rom[:-2]) & 65535).to_bytes(2, 'little')
    allowed.update([len(rom) - 2, len(rom) - 1])
    result = bytes(rom)
    changed = [i for i, (a, b) in enumerate(zip(baseline, result)) if a != b]
    require(all(i in allowed for i in changed), 'Unexpected binary modification')
    if not development:
        require(sha(result) == meta['target_sha256'], 'Output differs from the frozen test release. Use --development for intentional edits.')
    return meta, baseline, result, changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom', nargs='?', type=Path, default=ROOT / 'roms/original.ws')
    parser.add_argument('--out', type=Path, default=ROOT / 'build')
    parser.add_argument('--development', action='store_true', help='Label changed output DEV; bypass only the final release SHA lock')
    args = parser.parse_args()
    original = args.rom.read_bytes()
    meta, baseline, result, changes = build(original, args.development)
    name = f"Densha_de_Go_2_EN_v{meta['rom_version']}" + ('_DEV' if args.development else '')
    out = args.out.resolve()
    require(not out.is_relative_to(ROOT / 'patches'), 'Use a build directory, not the frozen patches directory')
    files = {name + '.ws':result}
    for label, source in [('CUMULATIVE', original), (f"from_v{meta['previous_rom_version']}_INCREMENTAL", baseline)]:
        for extension, lib in [('bps', bps), ('ips', ips)]:
            patch = lib.create(source, result)
            require(lib.apply(source, patch) == result, 'Patch roundtrip failed')
            files[f'{name}_{label}.{extension}'] = patch
    out.mkdir(parents=True, exist_ok=True)
    for filename, data in files.items():
        (out / filename).write_bytes(data)
    report = {'rom_version':meta['rom_version'], 'development':args.development, 'rom_sha256':sha(result), 'original_sha256':sha(original), 'baseline_sha256':sha(baseline), 'checksum':hex(int.from_bytes(result[-2:], 'little')), 'changes':changes, 'files':{n:sha(v) for n,v in files.items()}}
    (out / 'BUILD_REPORT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError) as error:
        print(f'Build failed: {error}', file=sys.stderr)
        sys.exit(1)
