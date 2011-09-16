# -*- coding: utf8 -*-
#
# Copyright 2011 Kyrre Ness Sjøbæk
# This file is part of AcdOpti.
#
#    AcdOpti is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    AcdOpti is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with AcdOpti.  If not, see <http://www.gnu.org/licenses/>.


from AcdOptiExceptions import AcdOptiException_dataDict_setValSingle,\
                               AcdOptiException_dataDict_getValsSingle,\
                               AcdOptiException_dataDict_stringWithSpace,\
                               AcdOptiException_fileParser_invalidMode,\
                               AcdOptiException_fileParser_invalidSyntax
                             
import exceptions
import re
#from collections import defaultdict

#whitespace = (" ", "\n", "\t") #What is regarded as whitespace?

parserDebug = False #Set this to True to print extra stuff for debugging, False to disable

class DataDict():
    """
    Multimap-like order-preserving storage.
    Expects keys must be strings, vals must be strings and DataDicts.
    Strings can't start or end with whitespace.
    """
    keys = None
    vals = None
    length = None
    def __init__(self):
        self.keys = []
        self.vals = []
        self.length = 0

    @staticmethod
    def keyValidCheck(key):
        "Checks that the key is valid. Raises a TypeError if it isn't."
        if type(key) != str:
            raise TypeError("Key must be string, key=" + str(key))
        elif key.strip() != key:
            raise TypeError("Key can't start or end with whitespace")
    @staticmethod
    def valValidCheck(val):
        "Checks that the value is valid. Raises a Type error if it isn't"
        if type(val) == str:
            if val.strip() != val:
                raise TypeError("String value can't start or end with whitespace")
        elif not isinstance(val,DataDict):
            raise TypeError("Val must be of type string or DataDict, val=" + str(val))
    
    @staticmethod
    def boolconv(boolIn):
        """
        Helper function, converts the many shades of bool found into python's True/False
        """
        if boolIn == "True" or boolIn == "true" or boolIn == "1" or boolIn == "on":
            return True
        elif boolIn == "False" or boolIn == "false" or boolIn == "0" or boolIn == "off":
            return False
        else:
            raise TypeError("Input boolIn=" + str(boolIn) + " is invalid.")
    def pushBack(self, key, val):
        """
        Appends a (key,value) pair to the end of the storage,
        and returns the appended value.
        
        Raises TypeError if key or val is invalid.
        """
        #Input checking on key and val
        try:
            DataDict.keyValidCheck(key)  
            DataDict.valValidCheck(val)
        except TypeError as e:
            raise TypeError("Got a TypeError, key=\"" + str(key) + "\", val=\"" + str(val) + "\"", e.args)
        
        #Everything OK
        self.keys.append(key)
        self.vals.append(val)
        self.length += 1
        
        return val
    
    def getVals(self, key):
        """
        Returns a list with all values associated with a given key,
        in the order they where pushBack'ed.
        If there are no values, an empty list is returned. 
        """
        retBuf = []
        for i in xrange(len(self.keys)):
            if self.keys[i] == key:
                retBuf.append(self.vals[i])
        return retBuf
    
    def getValSingle(self,key):
        """
        Assuming that only one value are associated with
        the given key, return this value.
        If more than one or zero values where found,
        raise a AcdOptiException_dataDict_getValsSingle exception
        """
        vals = self.getVals(key)
        if len(vals) == 0:
            raise AcdOptiException_dataDict_getValsSingle("Key '" + key + "' yielded no hits")
        elif len(vals) > 1:
            raise AcdOptiException_dataDict_getValsSingle("Key '" + key + "' yielded more than one hit", vals)
        return vals[0]

    def __getitem__(self,entry):
        """
        If entry is a string, return the corresponding value (same behavior as getValSingle)
        If entry is an integer, return a 2-tuple (key,value).
        Raises TypeError or IndexError on bad input, and AcdOptiException_dataDict_getValsSingle
        if the data is missing or there is to much of it.
        """
        if type(entry) == int:
            if entry < 0 or entry > self.length:
                raise IndexError("Index='"+str(entry)+"' out of range [0,"+ str(self.length-1) +"]")
            return (self.keys[entry], self.vals[entry])
        elif type(entry) == str:
            return self.getValSingle(entry)
        else:
            raise TypeError("entry must be either string or int")
    
    def setValSingle(self, key, val):
        """
        Assuming that there is one and only one entry with this key,
        set its value to "val" (returning the old value).
        
        If none or multiple entries are encountered,
        raise a AcdOptiException_dataDict_setValSingle exception.
        If val is invalid, raise TypeError.
        """

        if DataDict.valValidCheck(val):
            raise TypeError(val)
        
        ii = None
        for i in xrange(self.length):
            if self.keys[i] == key:
                if ii:
                    raise AcdOptiException_dataDict_setValSingle("Multiple keys found")
                ii = i
        if ii == None:
            raise AcdOptiException_dataDict_setValSingle("No entries with key='" + key + "' found")
        
        ret = self.vals[ii]
        self.vals[ii] = val
        return ret
    
    def clear(self):
        """
        Deletes all keys/values stored
        """
        self.keys = []
        self.vals = []
        self.length = 0
    
    def delItem(self, key):
        """
        Delete the key/val(s) with a given key,
        which may be a string or an integer index.
        
        Returns a list of 2-tuples with removed key/vals
        """
        if type(key) == int:
            return [self.__killItem(key)]
        elif type(key) == str:
            ret = []
            found = True
            while found:
                found = False
                #Find the index
                for i in xrange(len(self)):
                    if self.keys[i] == key:
                        ret.append(self.__killItem(i))
                        found = True
                        break
                #END for i in len(self)
            #END while found
            return ret
        else:
            raise TypeError
    def __killItem(self,idx):
        """
        Helper method for delItem() which deletes
        a single key/val pair with a specific numeric index 'idx',
        returning a (key, val) 2-tuple.
        """
        ret = (self.keys[idx], self.vals[idx])
        del self.keys[idx]
        del self.vals[idx]
        self.length -= 1
        return ret
        
    def copy(self):
        """
        Returns a new DataDict which is are a recursive/deep copy of this one.
        """
        ret = DataDict()
        for item in self:
            if isinstance(item[1], DataDict):
                #The item is in itself a dataDict
                ret.pushBack(item[0], item[1].copy())
            else:
                #String
                ret.pushBack(item[0], item[1])
        return ret
    def __str__(self):
        """
        Returns a string representation of the dataDict
        """
        retrs = ""
        for i in xrange(self.length):
            if isinstance(self.vals[i], DataDict):
                retrs += "(\"" + self.keys[i] + "\" , " + str(self.vals[i]) + ") , "
            else:
                retrs += "(\"" + self.keys[i] + "\" , \"" + str(self.vals[i]) + "\") , "
        
        return "[" + retrs[:-3] + "]"
    def __iter__(self):
        return DataDictIter(self)
    def __len__(self):
        return self.length
class DataDictIter:
    """
    Iterator for looping through a dataDict.
    Yields a tuple (key, value) for each iteration.
    """
    dataDict = None
    idx =  None
    def __init__(self, dataDict):
        self.dataDict = dataDict
        self.idx = 0
    def next(self):
        if self.idx >= self.dataDict.length:
            raise StopIteration
        ret = (self.dataDict.keys[self.idx], self.dataDict.vals[self.idx])
        self.idx += 1
        return ret

class AcdOptiFileParser():
    """
    Base class for all file/stream parsers.
    All parsers, except baseclass,
    accepts the same __init__() arguments:
    - data: Either a filename pointing to the data,
        or a string with the same content as would a file,
        or a dataDict (in case of baseclass).
    - mode: A short string with flags indicating how
        to treat the data:
        "w"  : Writing a new file (if necessary truncating
            one that already excists) with whatever is then in dataDict
            when the function "write()" is called.
            Argument data is then the filename
        "r"  : Reads a file into dataDict
            Argument data is then the filename
        "rw" : Reads in init, then same behaviour as "w"
        "s"  : Same as "r", but data is a string containing
            data in the same format as would normally be used on disk
    
    To write data from a string or dataDict,
    first create one object of the correct input type
    then create another object in "w" mode for the output type,
    use importDataDict(), and then write().
    """
    
    dataDict = None
    
    def __init__(self,dataDict=None):
        print "AcdOptiFileParser::__init__()"
        """
        Baseclass does the same as children,
        but can't do file IO. This constructor
        may initialize from a dataDict.
        """
        self.importDataDict(dataDict)
        
    def importDataDict(self,dataDict_in=None):
        """
        This functions is usefull for converting between formats.
        Also used for initializing the dataDict.
        """
        print "AcdOptiFileParser::importDataDict()"
        if self.dataDict == None:
            self.dataDict = DataDict()
        if dataDict_in != None:
            for item in dataDict_in:
                self.dataDict.pushBack(item[0],item[1])
    #END importDataDict()
    
    def write(self):
        """
        If mode="w" or "rw", truncate and write to the specified file,
        else raise exception AcdOptiExceptions.AcdOptiException_fileParser_invalidMode
        """
        print "AcdOptiFileParser::write()"
        
        if self.mode != "w" and self.mode != "rw":
            raise AcdOptiException_fileParser_invalidMode(\
                "Got mode=\"" + self.mode + "\"")
        f = open(self.fname, 'w')
        f.write(repr(self))
        f.close()
    
    def __repr__(self):
        raise NotImplementedError

class AcdOptiFileParser_simple(AcdOptiFileParser):
    """
    Reads and writes ACD text files in the "simple" syntax,
    used by acdtool rfpost.
    
    Expected syntax example:
    key {
    key = value
    key2 = value //Comment
    }
    
    Tokens:
    * "{"  : Start of sub-dict
    * "}"  : End of sub-dict
    * "\n" : If within a dict, separate two key/value pairs.
        Insignificant when before { and } 
    * "="  : Separates key/value within a dict
    * "//" : Ignore the rest of this line
    * "{(arbitary ammount of whitespace)}" : Value is an empty string
    Other rules:
    Whitespace at beginning and end of key and value is ignored
    """
        
    fname = None
    mode = None
    
    def __init__(self,data,mode):
        print "AcdOptiFileParser_simple::__init__()"
        self.mode = mode
        
        if mode == "s":
            data_parsed = AcdOptiFileParser_simple.parse(data) #May throw exception!
            self.importDataDict(data_parsed)
        elif mode == "r" or mode == "rw":
            self.fname = data
            
            #Read file
            ifile = open(data, 'r')
            datastr = ifile.read()
            ifile.close()
            
            #Parse
            data_parsed = AcdOptiFileParser_simple.parse(datastr)
            self.importDataDict(data_parsed)
        elif mode == "w":
            self.fname = data

            #Create an empty dataDict
            self.importDataDict()
        else:
            raise AcdOptiException_fileParser_invalidMode
    
    def __repr__(self):
        """
        Creates and returns a string in the "simple" syntax
        in the same format as interpreted by parseString
        """
        print "AcdOptiFileParser_simple::__repr__()"
        return AcdOptiFileParser_simple.repr_lifter(self.dataDict)
            


    @staticmethod
    def parse(str_in):
        """
        Combines preprocess() and dictify() to generate a single DataDict.
        """
        print "AcdOptiFileParser_simple::parse()"
        tokenLines = AcdOptiFileParser_simple.preprocess(str_in)
        if parserDebug:
            AcdOptiFileParser_simple.tokenLinesPrettyPrint(tokenLines)
        
        dict = AcdOptiFileParser_simple.dictify(tokenLines)
        if parserDebug: print dict
        
        return dict
    
    @staticmethod
    def tokenLinesPrettyPrint(tokenLines):
        print "AcdOptiFileParser_simple::tokenLinesPrettyPrint()"
        print '"""'
        for idx in xrange(len(tokenLines)):
            print idx, "\t:\t", tokenLines[idx]
        print '"""'
    
    @staticmethod
    def preprocess(str_in):
        """
        This method accepts a string in the "simple" format,
        and preprocesses it. After preprocessing, the syntax is as follows:
        * No comments
        * All lines contains a key/value-pair OR a key / "{" pair OR a "}"
        * Always single space around "="
        * Always single space between key / "{"
        * No extra whitespace at beginning/end of line
        * No whitespace in "{}" (value is empty string) 
        
        Returns a list of lines, where the first level is the lines,
        and the second is the tokens on this line.
        Example1: " a =b//hei" is returned as ["a", "=", "b"],
        Example2: "key{" and "key\n{" is returned as ["key", "{"]
        Example3: "}" is returned as ["}"]    
        """
        print "AcdOptiFileParser_simple::preprocess()"
        
        #Strip comments, leading/trailing whitespace, and blank/comment lines
        str_in_strippedlines = []
        for line in str_in.splitlines():
            tmp = line.split("//")[0]
            tmp = tmp.strip()
            if tmp != "":
                str_in_strippedlines.append(tmp)
        if parserDebug: print "str_in_strippedlines =", str_in_strippedlines
        
        #Make sure that all lines are either "key = val", "key {" or "}"
        str_in_tokenLines = []
        for line in str_in_strippedlines:
            #if parserDebug: print "line =", line
            tokenLine = [line]
            if "=" in line:
                #key/val-pair
                tokenLine = map(lambda s: s.strip(), line.split("="))
                if "{" in line or "}" in line:
                    if re.match("{\s*}", tokenLine[1]):
                        # We have an "{}" in the line, after the "="
                        tmp = line.split("=")
                        tokenLine = [tmp[0].strip(), "{}"]
                    else:
                        raise AcdOptiException_fileParser_invalidSyntax("Can't have '{','}' and '=' on same line except for 'key = { }', line = '" + line + "'")
                if len(tokenLine) != 2:
                    raise AcdOptiException_fileParser_invalidSyntax("More than one '=' found in one line, line = " + line + "'")
                tokenLine = [tokenLine[0], "=", tokenLine[1]] #Insert the equality sign
            elif "{" in line:
                #Begin subdict ({} ruled out)
                if line == "{":
                    #Single "{" on line, append to previous line
                    if str_in_tokenLines[-1][-1] == "{":
                        raise AcdOptiException_fileParser_invalidSyntax("Double '{' encountered, line = '" + line + "'")
                    str_in_tokenLines[-1] += "{"
                    continue #We're done here
                elif re.match("[\w\s]*{", line):
                    #key/{ pair
                    tokenLine = [line[:-1].strip(), "{"]
                else:
                    #Something weird
                    raise AcdOptiException_fileParser_invalidSyntax("Extra '{' in line, line = '" + line + "'")
            # END if
            #if parserDebug: print "appending tokenLine =", tokenLine
            str_in_tokenLines.append(tokenLine)
        #END for line in str_in_strippedlines
        
        #Sanity check on output
        for line in str_in_tokenLines:
            if len(line) == 1 and line[0] != "}":
                raise AcdOptiException_fileParser_invalidSyntax("Error found in sanity check: single-entry != '}', line = '" + str(line) + "'")
            elif len(line) == 2 and line[1] != "{":
                raise AcdOptiException_fileParser_invalidSyntax("Error found in sanity check: double-entry with entry 2 != '{', line = '" + str(line) + "'")
            elif len(line) == 2 and "{" in line[0]:
                raise AcdOptiException_fileParser_invalidSyntax("Error found in sanity check: double-entry with entry 1 containing a '{', line = '" + str(line) + "'")
            elif len(line) == 3 and line[1] != "=":
                raise AcdOptiException_fileParser_invalidSyntax("Error found in sanity check: triple-entry with entry 2 != '=', line = '" + str(line) + "'")
            elif len(line) == 3 and reduce(lambda a, b: a and b, map(lambda c: "{" in c, line)):
                raise AcdOptiException_fileParser_invalidSyntax("Error found in sanity check: triple-entry containing a '{', line = '" + str(line) + "'")
            elif len(line) == 0 or len(line) > 3:
                raise AcdOptiException_fileParser_invalidSyntax("Error found in sanity check: Unexpected line  0 < entries <= 3 found, line ='" + str(line) + "'")
        #END for line in str_in_tokenLines
        openBraceCount = 0
        closeBraceCount =  0
        for line in str_in_tokenLines:
            if len(line) == 1:
                closeBraceCount += 1
            elif len(line) == 2:
                openBraceCount += 1
        if openBraceCount != closeBraceCount:
            raise AcdOptiException_fileParser_invalidSyntax("Unbalanced parenthesis, openBraceCount =", openBraceCount, ", closeBraceCount =", closeBraceCount)
        
        return str_in_tokenLines
    #END preprocess()
    
    @staticmethod
    def dictify(tokenLines):
        """
        Accepts a list of tokenized lines as produced by preprocess,
        turn it into a (tree of) DataDicts 
        """
        print "AcdOptiFileParser_simple::dictify()"
        if parserDebug: 
            print "Got tokenLines:"
            AcdOptiFileParser_simple.tokenLinesPrettyPrint(tokenLines)
            
        dictBuf = DataDict()
        
        idx = 0
        while idx < len(tokenLines):
            line = tokenLines[idx]

            if len(line) == 2:
                key = line[0]
                idx2 = idx+1
                depth = 1
                while depth > 0:
                    if idx2 == len(tokenLines):
                        AcdOptiFileParser_simple.tokenLinesPrettyPrint(tokenLines)
                        raise AcdOptiException_fileParser_invalidSyntax("Error found in dictify(): reached end of tokenLines without hitting closing '}'")
                    
                    line2 = tokenLines[idx2]
                    if line2 == ["}"]:
                        depth -= 1
                    elif len(line2) == 2 and line2[1] == "{":
                        depth += 1
                    idx2 += 1
                idx2 -= 1        
                val = AcdOptiFileParser_simple.dictify(tokenLines[idx+1:idx2])
                dictBuf.pushBack(key, val)
                idx = idx2
                
            elif len(line) == 3:
                if line[2] == "{}":
                    dictBuf.pushBack(line[0], "")
                else:
                    dictBuf.pushBack(line[0], line[2])
            idx += 1
        #END while
        if parserDebug: print "AcdOptiFileParser_simple::dictify(): returning dictBuf =", dictBuf
        return dictBuf
    #END dictify
    
    @staticmethod
    def repr_lifter(dataDict):
        """
        Function doing the real work for __repr__(),
        split into a separate function in order to be able to use it
        from *_Lua and *_KVC modules
        """
        print "AcdOptiFileParser_simple::repr_lifter()"
    
        retrs = ""
        d = 0; #Which depth are we operating in
        
        i = [] #Index into dataClass i[d]
        i.append(0)

        stack = []
        stack.append(dataDict)

        tab = 3*" "
        
        if dataDict.length == 0:
            #Corner case: Empty dataDict
            return ""

        #while i[0] < stack[0].length:
        while d >= 0:
            # print d, i[d], stack[d].length
                     
            #Get the next key
            key = stack[d].keys[i[d]]
            val = stack[d].vals[i[d]]
            
            if isinstance(val,DataDict):
                #Go one level deeper
                retrs += d*tab + key + "\n" + d*tab + "{\n"
                
                i[d] += 1
                d += 1
                stack.append(val)
                i.append(0)

            else:
                if val == "":
                    val = "{ }"
                retrs += d*tab + key + " = " + val + "\n"
                i[d] += 1
                
            # Pop finished dataDicts of the stack
            # print retrs
            # print d, i[d], stack[d].length
            while i[d] == stack[d].length: #and d != 0:
                stack.pop()
                i.pop()
                d -= 1
                # print "pop()", d
                if d != -1:
                    #Don't bracket the outer dataDict
                    retrs += d*tab + "}\n"
                    # print retrs
                else:
                    #Break the inner loop
                    break
            # print

        return retrs
    #END repr_lifter

class AcdOptiFileParser_Lua(AcdOptiFileParser):
    """
    Reads and writes ACD text files in the "Lua" syntax,
    also used by solver output file.
    """
    def __init__(self,data,mode):
        raise exceptions.NotImplementedError
    
    def write(self):
        raise exceptions.NotImplementedError


class AcdOptiFileParser_KVC(AcdOptiFileParser):
    """
    Reads and writes ACD text files in the "KVC" syntax,
    used by solver input params.
    
    It really uses the simple parser behind-the-scenes,
    with some pre/post-processing added, as the syntax is the same
    except LUA syntax adds a ":" between keys and values,
    such that it replaces "=" for normal key/val pairs,
    and is an additional character between Label and "{" for key/dict pairs. 
    
    Expected syntax example:
    Label : {
    field : value
    field2 : value //Comment
    }
    """
    def __init__(self,data,mode):
        print "AcdOptiFileParser_KVC::__init__(), mode=", mode
        self.mode = mode
        
        if mode == "s":
            data_parsed = AcdOptiFileParser_simple.parse(self.changeToSimple(data)) #May throw exception!
            self.importDataDict(data_parsed)
        elif mode == "r" or mode == "rw":
            self.fname = data
            
            #Read file
            ifile = open(data, 'r')
            datastr = ifile.read()
            ifile.close()
            
            #Parse
            data_parsed = AcdOptiFileParser_simple.parse(self.changeToSimple(datastr))
            self.importDataDict(data_parsed)
        elif mode == "w":
            self.fname = data

            #Create an empty dataDict
            self.importDataDict()
        else:
            raise AcdOptiException_fileParser_invalidMode
    
    def __repr__(self):
        print "AcdOptiFileParser_KVC::__repr__()"
        simpleRepr = AcdOptiFileParser_simple.repr_lifter(self.dataDict)
        return AcdOptiFileParser_KVC.changeFromSimple(simpleRepr)
        
    @staticmethod
    def changeToSimple(data):
        """
        Converts a string from "KVC" format to "simple"
        """
        data = re.sub(":\s*{", "{", data)
        #TODO: Problem - if there is a ":" in the string, we now have dual "=" -> Parser not happy.
        data = data.replace(":", "=") 
        return data
    @staticmethod
    def changeFromSimple(data):
        """
        Converts a string from "simple" to "KVC" format
        """
        data = data.replace("=", ":")
        data = re.sub("(\w)\s*{", r'\1 : {', data)
        return data