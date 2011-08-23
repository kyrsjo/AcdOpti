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
