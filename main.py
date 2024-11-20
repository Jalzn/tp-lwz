import argparse

from lwz import LZWCompressor

def main():
    parser = argparse.ArgumentParser(description='LZW Compression Algorithm')
    parser.add_argument('mode', choices=['compress', 'decompress'], help='Operation mode')
    parser.add_argument('input_file', help='Input file path')
    parser.add_argument('output_file', help='Output file path')
    parser.add_argument('--bits', type=int, default=12, help='Number of bits (default: 12)')
    parser.add_argument('--variable', action='store_true', help='Use variable-size encoding')
    parser.add_argument('--stats', action='store_true', help='Generate statistics')
    
    args = parser.parse_args()
    
    compressor = LZWCompressor(fixed_bits=args.bits, variable_size=args.variable)
    
    if args.mode == 'compress':
        compressor.compress(args.input_file, args.output_file)
    else:
        compressor.decompress(args.input_file, args.output_file)
    
    if args.stats:
        # Salvar estatísticas em arquivo
        import json
        stats_file = f"{args.output_file}.stats.json"
        with open(stats_file, 'w') as f:
            json.dump(compressor.stats, f, indent=2)

if __name__ == "__main__":
    main()
