"""
scoreth11.dat decoder. Pure stdlib, no package imports, so tools/scoredat.py can load it outside AP.
Format from ThScoreFileConverter (BSD-2-Clause), commit feb02e2fa390cd0e0c599c97cc12399d9c07fd22:
https://github.com/y-iihoshi/ThScoreFileConverter/tree/feb02e2fa390cd0e0c599c97cc12399d9c07fd22/ThScoreFileConverter/Models
(Th11/Converter.cs, Th095/HeaderBase.cs, ThCrypt.cs, Lzss.cs, Th10/Chapter.cs, Th10/ClearDataBase.cs, Th10/Practice.cs).
"""
import struct

HEADER_SIZE = 0x18  # "TH11", encoded_all_size, 2 unknown u32, encoded_body_size, decoded_body_size
CHUNK_HEADER_SIZE = 0x0C  # signature[2], version u16, checksum u32, size i32 (size includes this header)
CLEAR_SIGNATURE = b"CR"
CLEAR_SIZE = 0x68D4
CHARAS = ["ReimuYukari", "ReimuSuika", "ReimuAya", "MarisaAlice", "MarisaPatchouli", "MarisaNitori", "Total"]
LEVELS = ["Easy", "Normal", "Hard", "Lunatic"]
STAGES = [1, 2, 3, 4, 5, 6]
# CR chunk: chara i32, 5 levels x 10 rankings x 28 bytes, play count, play time, 5 clear counts, then practices.
PRACTICE_OFFSET = CHUNK_HEADER_SIZE + 4 + 5 * 10 * 28 + 4 + 4 + 5 * 4  # 0x5A4
PRACTICE_SIZE = 8  # score/10 u32, cleared u8, unlocked u8, u16 padding; levels outer, stages inner


def _decrypt(body: bytes, key=0xAC, step=0x35, block=0x10) -> bytes:
	"""ThCrypt.Decrypt with limit == size: each block's bytes are de-interleaved back to front."""
	size = len(body)
	addup = size % block
	if addup >= block // 4:
		addup = 0
	addup += size % 2
	out, pos, size = bytearray(), 0, size - addup
	while size > 0:
		block = min(block, size)
		chunk, dec = body[pos:pos + block], bytearray(block)
		i = 0
		for j in range(2):
			o = block - j - 1
			for _ in range((block - j + 1) // 2):
				dec[o] = chunk[i] ^ key
				i, o, key = i + 1, o - 2, (key + step) & 0xFF
		out += dec
		pos, size = pos + block, size - block
	return bytes(out + body[pos:])


def _decompress(data: bytes) -> bytes:
	"""LZSS: 13-bit offsets into an 0x2000 dictionary (write index starts at 1), 4-bit length + 3; offset 0 ends."""
	data += b"\0" * 4  # BitReader reads zeros past EOF, i.e. the end marker (flag 0, offset 0)
	pos = 0

	def read(n):  # MSB-first bits
		nonlocal pos
		value = 0
		for _ in range(n):
			value = value << 1 | (data[pos >> 3] >> (7 - (pos & 7))) & 1
			pos += 1
		return value

	out, dic, index = bytearray(), bytearray(0x2000), 1
	while True:
		if read(1):
			ch = read(8)
			out.append(ch)
			dic[index], index = ch, (index + 1) & 0x1FFF
			continue
		offset = read(13)
		if offset == 0:
			return bytes(out)
		for i in range(read(4) + 3):
			ch = dic[(offset + i) & 0x1FFF]
			out.append(ch)
			dic[index], index = ch, (index + 1) & 0x1FFF


def decode(raw: bytes) -> bytes:
	"""Encrypted file -> header + decompressed body (ThScoreFileConverter's th11decoded.dat)."""
	signature, all_size, _, _, body_size, decoded_size = struct.unpack_from("<4si2I2i", raw)
	if signature != b"TH11" or all_size != len(raw) or all_size - body_size != HEADER_SIZE:
		raise ValueError(f"not a TH11 score file (signature {signature!r}, size {all_size} vs file {len(raw)})")
	body = _decompress(_decrypt(raw[HEADER_SIZE:]))
	if len(body) != decoded_size:
		raise ValueError(f"decompressed {len(body)} bytes, header says {decoded_size}")
	return raw[:HEADER_SIZE] + body


def chunks(decoded: bytes):
	"""Decoded file -> [(signature, offset, size, body)]; body is the whole chunk including its header."""
	result, offset = [], HEADER_SIZE
	while offset < len(decoded):
		signature, _, checksum, size = struct.unpack_from("<2sHIi", decoded, offset)
		if size < CHUNK_HEADER_SIZE or offset + size > len(decoded):
			raise ValueError(f"bad chunk size {size} at 0x{offset:X}")
		body = decoded[offset:offset + size]
		if sum(body[8:]) != checksum:  # checksum covers size field + data
			raise ValueError(f"bad checksum for {signature!r} at 0x{offset:X}")
		result.append((signature.decode("ascii"), offset, size, body))
		offset += size
	return result


def chara(chunk: bytes) -> str:
	index = struct.unpack_from("<i", chunk, CHUNK_HEADER_SIZE)[0]
	return CHARAS[index] if 0 <= index < len(CHARAS) else str(index)


def practice_progress(chunk: bytes) -> dict:
	"""CR chunk -> {difficulty: {stage: (unlocked, cleared, score)}}; score as shown in game (stored / 10)."""
	if chunk[:2] != CLEAR_SIGNATURE or len(chunk) != CLEAR_SIZE:
		raise ValueError("not a TH11 clear-data chunk")
	result, offset = {}, PRACTICE_OFFSET
	for level in LEVELS:
		result[level] = {}
		for stage in STAGES:
			score, cleared, unlocked = struct.unpack_from("<IBB", chunk, offset)
			result[level][stage] = (unlocked, cleared, score * 10)
			offset += PRACTICE_SIZE
	return result
