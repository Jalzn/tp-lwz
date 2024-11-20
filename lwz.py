import time
import struct
import os

from trie import Trie

class LZWCompressor:
    def __init__(self, fixed_bits: int = 12, variable_size: bool = False):
        self.fixed_bits = fixed_bits
        self.variable_size = variable_size
        self.stats = {
            'compression_ratio': 0,
            'dictionary_size': 0,
            'execution_time': 0,
            'input_size': 0,
            'output_size': 0
        }
        
    def _init_dictionary(self) -> Trie:
        dictionary = Trie()
        for i in range(256):
            dictionary.insert(chr(i), i)
        return dictionary
    
    def _get_current_bits(self, code: int) -> int:
        if self.variable_size:
            return max(9, (code.bit_length()))
        return self.fixed_bits
    
    def compress(self, input_file: str, output_file: str) -> None:
        start_time = time.time()
        
        dictionary = self._init_dictionary()
        next_code = 256
        current_string = ""
        
        with open(input_file, 'rb') as f_in, open(output_file, 'wb') as f_out:
            f_out.write(struct.pack('<?i', self.variable_size, self.fixed_bits))
            
            bit_buffer = 0
            bit_count = 0
            
            self.stats['input_size'] = os.path.getsize(input_file)
            
            while True:
                byte = f_in.read(1)
                if not byte:
                    break
                    
                char = byte.decode('latin-1')
                temp_string = current_string + char
                
                if dictionary.search(temp_string) is not None:
                    current_string = temp_string
                else:
                    code = dictionary.search(current_string)
                    
                    bits_needed = self._get_current_bits(next_code)
                    
                    bit_buffer = (bit_buffer << bits_needed) | code
                    bit_count += bits_needed
                    
                    while bit_count >= 8:
                        output_byte = (bit_buffer >> (bit_count - 8)) & 0xFF
                        f_out.write(bytes([output_byte]))
                        bit_count -= 8
                        bit_buffer &= (1 << bit_count) - 1
                    
                    if next_code < (1 << self.fixed_bits):
                        dictionary.insert(temp_string, next_code)
                        next_code += 1
                    
                    current_string = char
                    
                    self.stats['dictionary_size'] = dictionary.get_size()
                    self.stats['compression_ratio'] = os.path.getsize(output_file) / self.stats['input_size']
            
            if current_string:
                code = dictionary.search(current_string)
                bits_needed = self._get_current_bits(next_code)
                bit_buffer = (bit_buffer << bits_needed) | code
                bit_count += bits_needed
                
                while bit_count > 0:
                        shift = min(bit_count, 8)
                        output_byte = (bit_buffer >> (bit_count - shift)) & 0xFF
                        f_out.write(bytes([output_byte]))
                        bit_count -= shift
                        bit_buffer &= (1 << bit_count) - 1 if bit_count > 0 else 0
        
        self.stats['execution_time'] = time.time() - start_time
        self.stats['output_size'] = os.path.getsize(output_file)

    def decompress(self, input_file: str, output_file: str) -> None:
        start_time = time.time()
        
        dictionary = {i: bytes([i]).decode('latin-1') for i in range(256)}
        next_code = 256
        
        with open(input_file, 'rb') as f_in, open(output_file, 'wb') as f_out:
            variable_size, fixed_bits = struct.unpack('<?i', f_in.read(5))
            
            bit_buffer = 0
            bit_count = 0
            
            while bit_count < fixed_bits:
                byte = f_in.read(1)
                if not byte:
                    return
                bit_buffer = (bit_buffer << 8) | int.from_bytes(byte, 'big')
                bit_count += 8
            
            old_code = bit_buffer >> (bit_count - fixed_bits)
            bit_count -= fixed_bits
            bit_buffer &= (1 << bit_count) - 1
            
            f_out.write(dictionary[old_code].encode('latin-1'))
            
            while True:
                bits_needed = self._get_current_bits(next_code)
                while bit_count < bits_needed:
                    byte = f_in.read(1)
                    if not byte:
                        return
                    bit_buffer = (bit_buffer << 8) | int.from_bytes(byte, 'big')
                    bit_count += 8
                
                code = bit_buffer >> (bit_count - bits_needed)
                bit_count -= bits_needed
                bit_buffer &= (1 << bit_count) - 1
                
                if code not in dictionary:
                    string = dictionary[old_code] + dictionary[old_code][0]
                else:
                    string = dictionary[code]
                
                f_out.write(string.encode('latin-1'))
                
                if next_code < (1 << fixed_bits):
                    dictionary[next_code] = dictionary[old_code] + string[0]
                    next_code += 1
                
                old_code = code

        self.stats['execution_time'] = time.time() - start_time
