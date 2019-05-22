# Huffman-Compressor
Python application that compresses and decompresses files using the Huffman Compression algorithm

Compressed files are saved as .hfm files for convenience. The program will store the compressed data and the relevant decoding information in the file, so the hfm files can be decompressed at any time.
All types of files are supported.

During compression the program will display the number of bytes of data originally present and the number of bytes the data has been reduced to. While the program works for any file type, there is a good chance that files with lots of unique data will not be compressed by much, and the overhead of storing decompression information may be larger than the gains from compression

todos: increase speed, reduce overhead
