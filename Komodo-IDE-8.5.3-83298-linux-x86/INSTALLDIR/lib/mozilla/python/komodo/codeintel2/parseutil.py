#!/usr/bin/env python
# Copyright (c) 2004-2006 ActiveState Software Inc.
#
# Some CILE parsing utils extracted originally from phpcile and jscile
# but mostly generally useful to CILEs implemented in Python.


import codecs
import locale
import re
import sys
import os

from codeintel2.common import CILEError



#---- exported routines

def tryEncoding(buffer, encoding):
    """ buffer, encoding -> encoding_buffer

        Attempts to encode the buffer using the specified encoding

        Returns None on failure, a Unicode version of the buffer on success.
    """
    #log.info("_tryEncoding...%s",encoding)
    try:
        secret_decoder_ring = codecs.lookup(encoding)[1]
    except LookupError, e:
        # the encoding name doesn't exist, likely a pep263 failure
        # an example is using windows-1250 as the name
        return None
    try:
        (outdata,len) = secret_decoder_ring(buffer)
        return outdata
    except Exception, e: # Figure out the real exception types
        return None


try:
    _defaultEncoding = locale.getdefaultlocale()[1]
except ValueError:
    _defaultEncoding = None
if _defaultEncoding is not None:
    _defaultEncoding = _defaultEncoding.lower()

def getEncodedBuffer(buffer):
    decodedBuffer = tryEncoding(buffer, 'utf-8')
    if decodedBuffer is not None:
        return (decodedBuffer, 'utf-8', '')
    if _defaultEncoding is not None:
        decodedBuffer = tryEncoding(buffer, _defaultEncoding)
        if decodedBuffer is not None:
            return (decodedBuffer, _defaultEncoding, '')
    return (tryEncoding(buffer, 'iso8859-1'), 'iso8859-1', '')             



def urlencode_path(s):
    """URL-encode the given path string.
    
    This URL-encoding attempts to NOT encode characters that are typically
    legal path characters, e.g. '/', '\\', ':'. This is so that the result
    can more naturally be used as a filepath argument.
    
    The string must be an 8-bit string (that is all that URL-encoding can
    handle).
    """
    from urllib import quote
    safe = os.sep + (os.altsep or '') + ":"
    return quote(s, safe=safe)


#---- javadoc parsing

_javadoc1 = re.compile(r'\s*\/\*(.*)\*\/', re.S)
_javadoc2 = re.compile(r'^(\s*\*)', re.M)
_linedoc = re.compile(r'^(\s*#|\s*\/\/)', re.M)
_indent = re.compile(r'^([ \t]*)', re.M)
_param = re.compile(r'^\s*@param\s+(?P<type>[\w\\]+)\s+\$(?P<name>\w+)(?:\s+?(?P<doc>.*?))?', re.M|re.U)
_return = re.compile(r'^\s*@return\s+(?P<type>[\w\\]+)(?:\s+(?P<doc>.*))?', re.M|re.U)

def uncommentDocString(doc):
    # remove block style leading and end comments
    d = '\n'.join(re.findall(_javadoc1, doc))
    if d:
        # remove starting * if javadoc style
        d = re.sub(_javadoc2,'',d)
    else:
        d = doc
        # remove line style comments
        d = re.sub(_linedoc,'',d)


    # trim preceeding blank lines.  we dont want to trim the first non-blank line
    lines = d.split('\n')
    while len(lines) and not lines[0].strip():
        lines.pop(0)
    d = '\n'.join(lines)
    
    # trip any blank end lines
    d = d.rstrip()
    
    # guess the indent size    
    spaces = re.findall(_indent, d)
    indent = spaces[0]
    for s in spaces:
        if len(s) and len(s) < indent:
            indent = len(s)

    # dedent the block
    if not indent:
        return d
    dedent = re.compile(r'^([ \t]{%d})' % indent, re.M)
    d = re.sub(dedent, '', d)
    return d

def parseDocString(doc):
    d = uncommentDocString(doc)
    params = re.findall(_param, d)
    result = re.findall(_return, d)
    if result:
        result = result[0]
    return (d, params, result)



SKIPTOK = 0x01 # don't consider this a token that is to be considered a part of the grammar, like '\n'
MAPTOK = 0x02  # use the token associated with the pattern when it matches
EXECFN= 0x04   # execute the function associated with the pattern when it matches
USETXT = 0x08  # if you match a single character and want its ascii value to be the token

class recollector:
    def __init__(self):
        self.res = {}
        self.regs = {}
        
    def add(self, name, reg, mods=None ):
        self.regs[name] = reg % self.regs
        #print "%s = %s" % (name, self.regs[name])
        if mods:
            self.res[name] = re.compile(self.regs[name], mods) # check that it is valid
        else:
            self.res[name] = re.compile(self.regs[name]) # check that it is valid

# Lexer class borrowed from the PyLRd project,
# http://starship.python.net/crew/scott/PyLR.html
class Lexer:
    eof = -1

    def __init__(self):
        self.tokenmap = {}
        self.prgmap = {}
        self.prglist = []
        self.lasttok = -1
        self.text = ""
        self.textindex = 0
        self.tokennum2name = {}

    def nexttok(self):
        self.lasttok = self.lasttok + 1
        return self.lasttok

    def settext(self, t):
        self.text = t
        self.textindex = 0

    def addmatch(self, prg, func=None, tokname="", attributes=MAPTOK|EXECFN):
        self.prglist.append(prg)
        tok = -2
        if not func:
            attributes = attributes & ~EXECFN
        if not tokname:
            attributes = attributes & ~MAPTOK
        if attributes & MAPTOK:
            self.tokenmap[tokname] = tok = self.nexttok()
        else:
            tok = self.nexttok()
        self.prgmap[prg] = tok, attributes, func
        self.tokennum2name[tok] = tokname

    def scan(self):
        for prg in self.prglist:
            mo = prg.match(self.text, self.textindex)
            if not mo: 
                continue
            self.textindex = self.textindex + len(mo.group(0))
            tmpres = mo.group(0)
            t, attributes, fn = self.prgmap[prg]
            #log.debug("'%s' token: %r", self.tokennum2name[t], tmpres)
            if attributes & EXECFN:
                tmpres = apply(fn, (mo,))
            if attributes & USETXT:
                t = ord(mo.group(0)[0])
            return (t, tmpres)
        if self.textindex >= len(self.text):
            return (self.eof, "")
        raise CILEError("Syntax Error in lexer")

