# standart modules
import struct

# addon modules
from .. import log


class PackedWriter():
    def __init__(self):
        self.data = bytearray()

    def putp(self, pkw):
        self.data += pkw.data

    def putf(self, fmt, *args):
        self.data += struct.pack(fmt, *args)

    def putv3f(self, vec):
        # write vertex coord
        self.data += struct.pack('<3f', vec[0], vec[2], vec[1])

    def puts(self, string):
        try:
            self.data += string.encode('cp1251')
        except UnicodeEncodeError:
            raise log.AppError('Not valid string: {}'.format(string))
        self.data += b'\x00'

    def replace(self, offset, byte_list):
        for byte_index, byte in enumerate(byte_list):
            self.data[offset + byte_index] = byte


class ChunkedWriter():
    def __init__(self):
        self.data = bytearray()

    def put(self, cid, writer):
        self.data += struct.pack('<2I', cid, len(writer.data))
        self.data += writer.data
