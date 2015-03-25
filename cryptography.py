# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 17:36:50 2015

custom encryption using feistel network as framework

@author: qingwei
"""

import math
import random
import binascii
from bitarray import bitarray

# data is bit array, which is array of boolean

# meta data
block_size = 128
key_size = int(block_size/2)
size_per_char = 8
char_per_block = int(block_size/size_per_char)

# self created s-box
sbox = {
    "00": {
        "00": "0101",
        "01": "1110",
        "10": "1100",
        "11": "0100"
        },
    "01": {
        "00": "1111",
        "01": "0001",
        "10": "1101",
        "11": "1011"
        },
    "10": {
        "00": "0111",
        "01": "1000",
        "10": "0000",
        "11": "1010"
        },
    "11": {
        "00": "0010",
        "01": "1001",
        "10": "0011",
        "11": "0110"
        }
    }

def rightHalf(arr):
    n = len(arr)    
    if n%2 == 1:
        raise ValueError("array length should be even")    
    return arr[:int(n/2)]

def leftHalf(arr):
    n = len(arr)    
    if n%2 == 1:
        raise ValueError("array length should be even")    
    return arr[int(n/2)-1:]

def swapLeftRight(arr):
    """swap the right halves and left halves of arr"""
    n = len(arr)    
    if n%2 == 1:
        raise ValueError("array length should be even")    
    left = leftHalf(arr)
    right = rightHalf(arr)
    return left.extend(right)

def round_function(inputText, operation, key):
    """
    round function of feistel network
    operation should accept half of text and key
    """
    newLeft = rightHalf(inputText)
    newRight = xor(operation(leftHalf(inputText), key), rightHalf(inputText))
    newLeft.extend(newRight)
    return newLeft
    pass

def xor(a, b):
    """a and b should be iterable of equal len"""
    for i,j in zip(a, b):
        if i!=j:
            yield 1
        else:
            yield 0
            
def key_generator(key, n):
    """return a generator of keys in """
    random.seed(key)
    for i in range(0, n):
        k = random.randrange(0, 128, 1)
        k = '{0:08b}'.format(k)
        yield bitarray(k)
        
def feistel_network_flow(bittext, operation, iteration, keys):
    """
    flow can be used for encryption and decryption by reversing order of keys
    bittext is bitarray, operation is function(bittext, operation)
    """
    intermediate = bittext  #initialize
    for k in keys:
        intermediate = round_function(intermediate, operation, k)
        
    return swapLeftRight(intermediate)
    
def substitution1(text, key):
    """
    text and key are 64 bit array (cut into half)
    1. find parity of the key
    2. if parity is odd, sub only 1st 2 bit of each entry
    3. if parity is even, sub only last 2 bit of each entry
    4. 
    """
    cipher = bitarray()
    n = len(text)   # should be 64
    parity = key.count(1)%1
    
    for i in range(0, n, 4):
        sub_unit = sboxlookup(text[i: i+4], key[i: i+4], parity)
        cipher.extend(sub_unit)
        
    return cipher
    pass

def sboxlookup(text4bit, key4bit, odd):
    """
    lookup the table and return the substitution
    """
    k = bitarray()
    t = bitarray()
    if odd:
        k.append(key4bit[0]).append(key4bit[2])
        t.append(text4bit[1]).append(text4bit[3])
    else:
        k.append(key4bit[1]).append(key4bit[3])
        t.append(text4bit[0]).append(text4bit[2])
        
    sub_str = sbox[k.to01()][t.to01()]
    sub = bitarray(sub_str)    
    
    return sub

def permutation1(text, key):
    """
    perform permutation by changing position of text bit
    both text and key have same length = 64
    """
    n = len(key)
    li = [i for i in range(0, n)]
    neworder = reorder_list(li, key)
    
    cipher = bitarray()
        
    for i in neworder:
        cipher.append(text[i])
        
    return cipher

def reorder_list(li, key):
    """
    both list and key should be array with same length, 
    key's element should be boolean
    """
    reordered = []
    while len(reordered) != len(key):
        li_len = len(li)        # len of current li, should decrease every iteration
        key = shift_arr(key, 3) # key need to be different every iteration
        index_2_select = int(key.to01(), 2) % li_len
        reordered.append(li[index_2_select])
        li.remove(li[index_2_select])   # remove the used value

    return reordered

def shift_arr(arr, n):
    """shift array n slot in round-robin fashion"""
    l = arr[-n:]
    l.extend(arr[:-n])
    return l