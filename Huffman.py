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

def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size

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

def addnode(node,node_q):
    if(len(node_q)<1):
        node_q.append(node)
        #print("Last node in")
    else:
        i = 0
        while(i<len(node_q) and node_q[i].freq<node.freq):
            i+=1
        node_q.insert(i,node)
        #print("Inserted at:",i)
    return node_q
        
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
    #nodes = nodes[::-1]
    while len(nodes)>1:
        node_a = nodes[0]
        node_b = nodes[1]
        nodes = nodes[2:]
        new_node = JoinNodes(node_a,node_b)
        nodes = addnode(new_node,nodes)
        #nodes = nodes + [new_node]
            
    root = nodes[0]
    root.code = ''
    computecode(root)
    inorder(root,encoder)
    #inorder_print(root)
    encoded_data = ''
    for char in data:
        encoded_data+=encoder[char]
    
    #print(encoder)
    return encoder
'''
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
'''

def HuffDecode(text,encoder,length,padding):
    decoded = bytearray()
    bintext = ''
    p = dict(zip(encoder.values(),encoder.keys()))
    keys = p.keys()
    #print(p)
    '''
    for i in text:
        bintext += str(i)
        #bintext+= bin(int.from_bytes(i, 'little'))[2:]
    bintext = bintext[:length-padding]
    '''
    k = ''
    for i in range(len(text)):
        k+=text[i]
        if k in keys:
            decoded+=bytearray(p[k])
            k = ''
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
        #self.tree = None
        self.padding = 0
        #self.length = 0
        self.encoder = []

def EncodeFile(filename):
    obj = EncodedObject()
    text = []
    start = time.time()
    print("Compressing file :",filename)
    with open(filename, 'rb') as file:
        for byte in iter(partial(file.read, 1), b''):
            text.append(byte)
    print("No of bytes processed in file:",len(text))
    obj.fname = filename
    newfile = filename.split(".")[0] +".hfm"
    obj.encoder = HuffEncode(text)
    for byte in text:
        obj.data += obj.encoder[byte]
    obj.padding = 8-(len(obj.data)%8)
    obj.data += "0"*obj.padding
    #print(obj.data)
    #obj.length = len(obj.data)
    b = bytearray()
    for i in range(0,len(obj.data),8):
        b.append(int(obj.data[i:i+8],2))
    obj.data = b
    #obj.data = int(obj.data[::-1], 2).to_bytes(obj.length//8, 'little')
    #print(obj.data)
    with open(newfile,"wb") as f:
        pickle.dump(obj,f)
     #print(text)
    print("No of bytes in compressed data:",len(obj.data))
    print("Object size:",get_size(obj))
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
    bintext = ''
    length = len(obj.data)
    padding = obj.padding
    #print(obj.data)
    for i in obj.data:
        #print(i)
        #bintext += bin(int.from_bytes(i, 'little'))[2:]
        temp = str(bin(i)[2:])
        bytestring = '0'*(8-len(temp))+temp
        #print(i,temp,bytestring)
        #temp = '0'*(8-(len(temp)%8)) + temp
        bintext += bytestring
        
    bintext = bintext[0:len(bintext)-padding]
    #print(bintext)
    decoded = HuffDecode(bintext,obj.encoder,length,obj.padding)
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
