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


import acdOpti.AcdOptiProject as optiProj
import acdOpti.AcdOptiFileParser as acdFile
import acdOpti.AcdOptiExceptions as optiEx
import shutil

while True:
    folderName = "test"
    try:
        a = optiProj.AcdOptiProject(folderName, True)
        break
    except optiEx.AcdOptiException_project_folderExists:
        print "Folder " + folderName + " already exists"
        print "Remove folder? [y/N]"
        inp = raw_input()
        if inp == "y":
            shutil.rmtree(folderName)
        else:
            break
        
    except optiEx.AcdOptiException_project_folderNotFound:
        print "Not found"
        break
    

# teststr = \
# """
# a =123   
# b{  //erjklgdfhgkhj
# c =345 //NoGood sgfsdfg 
#  fasd = 23u49823
# aef { 
# asd = 324
# }
#  }
# d = 12
# """
# print teststr
# print "Running:"
# testRead = acdFile.AcdOptiFileParser_simple(teststr, "s")
# print testRead.dataDict
# print testRead.__repr__()

# rfPost = acdFile.AcdOptiFileParser_simple("rfPost.in", "r")
# print rfPost.dataDict
# print rfPost.__repr__()
