# -*- coding: cp1252 -*-

import collections
import pickle
from functools import partial

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
    #print(data)
    encoded = {}
    encoder = {}
    for char in data:
        #char = chr(char)
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
        #char = chr(char)
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
            #print(node.char,end='')
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

def EncodeFile(filename):
    obj = EncodedObject
    '''
    with open(filename,'r',encoding='ansi') as f:
        text = f.read()
    '''
    text = []
    with open(filename, 'rb') as file:
        for byte in iter(partial(file.read, 1), b''):
            text.append(byte)
    obj.fname = filename
    newfile = filename.split(".")[0] +".hfm"
    print("Compressing file :",filename)
    print("Compressed filename:",newfile)
    obj.data,obj.tree = HuffEncode(text)
    with open(newfile,"wb") as f:
        pickle.dump(obj,f)
#use ansi
def DecodeFile(filename):
    with open(filename,'rb') as f:
        obj = pickle.load(f)
    oldf = obj.fname
    oldf = oldf.split(".")
    newf = oldf[0]+"_decompressed."+oldf[1]
    raw = HuffDecode(obj.data,obj.tree)
    '''
    with open(newf,"w",encoding='ansi') as f:
        f.write(raw)
    '''
    with open(newf,"wb") as f:
        f.write(raw)


#testfile = 'test.txt'
testfile = "ESA- Project Submission Presentation 2019.pptx"
#testfile = 'MP_Report.docx'
#testfile = 'lul.jpg'
EncodeFile(testfile)
print("Compressed")
#DecodeFile("lul.hfm")
#DecodeFile("test.hfm")
DecodeFile("ESA- Project Submission Presentation 2019.hfm")
#DecodeFile('MP_Report.hfm')
print("Decompressed")
