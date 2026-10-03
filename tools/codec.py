from collections import defaultdict, deque

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
