import collections
import pickle
import time
from functools import partial
from  tkinter import *
from tkinter.filedialog import askopenfilename
import sys
import os
root = Tk()
root.lift()
root.withdraw()

def computecode(node):
    if node.left!=None:
        node.left.code = node.left.parent.code + '0'
        computecode(node.left)
    if node.right!=None:
        node.right.code = node.right.parent.code + '1'
        computecode(node.right)

def inorder(node,d):
    if node!=None:
        inorder(node.left,d)
        if node.char!='':
            d[node.char] = node.code
        inorder(node.right,d)

def inorder_print(node):
    if node!=None:
        inorder_print(node.left)
        if node.char!='':
            print(node.char,":",node.code)
        inorder_print(node.right)
        
def HuffEncode(data):
    encoded = {}
    encoder = {}
    for char in data:
        if char not in encoded.keys():
            encoded[char]=1
        else:
            encoded[char]+=1
    encoded = collections.OrderedDict(sorted(encoded.items(), key=lambda kv: kv[1]))
    
    nodes = []
    for k in encoded.keys():
        node = HuffNode()
        node.char = k
        node.freq = encoded[k]
        nodes.append(node)
    while len(nodes)>1:
        node_a = nodes[0]
        node_b = nodes[1]
        nodes = nodes[2:]
        new_node = JoinNodes(node_a,node_b)
        nodes = [new_node]+nodes
    root = nodes[0]
    root.code = ''
    computecode(root)
    inorder(root,encoder)
    encoded_data = ''
    for char in data:
        encoded_data+=encoder[char]
    return encoded_data,root

def HuffDecode(text,tree):
    decoded = b''
    node = tree
    for i in range(len(text)):
        if text[i] == '0':
            node = node.left
        if text[i] == '1':
            node = node.right
        if node.char!='':
            decoded+=node.char
            node = tree
    return decoded
        

def JoinNodes(node_a,node_b):
    if node_a.freq>node_b.freq:
        node_a,node_b = node_b,node_a
    root = HuffNode()
    root.freq = node_a.freq + node_b.freq
    root.left = node_a
    root.right = node_b
    node_a.parent = root
    node_b.parent = root
    return root


class HuffNode:
    def __init__(self):
        self.char = ''
        self.freq = 0
        self.right = None
        self.left = None
        self.parent = None

    
def bits2string(b=None):
    return ''.join([chr(int(x, 2)) for x in b])

class EncodedObject:
    def __init__(self):
        self.fname = ''
        self.data = ''
        self.tree = None
        self.padding = 0
        self.length = 0

def EncodeFile(filename):
    obj = EncodedObject
    text = []
    start = time.time()
    print("Compressing file :",filename)
    with open(filename, 'rb') as file:
        for byte in iter(partial(file.read, 1), b''):
            text.append(byte)
    obj.fname = filename
    newfile = filename.split(".")[0] +".hfm"
    obj.data,obj.tree = HuffEncode(text)
    obj.padding = 8-len(obj.data)%8
    obj.data += "0"*obj.padding
    obj.length = len(obj.data)
    obj.data = int(obj.data[::-1], 2).to_bytes(obj.length//8, 'little')
    with open(newfile,"wb") as f:
        pickle.dump(obj,f)
    print("Object size:",sys.getsizeof(obj))
    print("File size:",os.stat(newfile).st_size)
    print("Compression complete! Time taken: %.2f seconds"%(time.time()-start))
    print("Compressed filename:",newfile)

def DecodeFile(filename):
    start = time.time()
    with open(filename,'rb') as f:
        obj = pickle.load(f)
    oldf = obj.fname
    oldf = oldf.split(".")
    newf = oldf[0]+"_decompressed."+oldf[1]
    fmstring = '0'+str(obj.length)+'b'
    padded_str = format(int.from_bytes(obj.data, 'little'), fmstring)[::-1]
    raw = padded_str[:obj.length-obj.padding]
    decoded = HuffDecode(raw,obj.tree)
    with open(newf,"wb") as f:
        f.write(decoded)
    print("Deompression complete! Time taken: %.2f seconds"%(time.time()-start))
    print("Decompressed filename:",newf)


print('Enter:\n1 to compress a file\n2 to decompress a hfm file\nAnything else to exit')
while True:
    choice = int(input(">>"))
    if choice == 1:
        print("Select the file to compress")
        root.filename = askopenfilename(title = "choose a file")
        file = root.filename
        root.withdraw()
        EncodeFile(file)
    elif choice == 2:
        print("Select the file to decompress")
        root.filename =  askopenfilename(title = "choose a file",filetypes = [("Huffman Compressed","*.hfm")])
        file = root.filename
        root.withdraw()
        DecodeFile(file)
    else:
        break
