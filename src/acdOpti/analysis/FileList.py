from AnalysisInterface import AnalysisInterface
from acdOpti.AcdOptiFileParser import DataDict

import os

class FileList(AnalysisInterface):
    """
    Simple analysis that lists the files in the finished folder
    """
    
    def __init__(self, folder, name):
        print "FileList::__init()"
        self.type     = "FileList"
        self.folder   = folder
        self.instName = name
        
        f = open(os.path.join(folder, name), 'r')
        print "In file: '" + f.read() + "'"
        f.close()
        
        self.lockdown = False
    
    @staticmethod
    def createNew(folder,name=None):
        #Just create a dummy file in the folder to indicate that the analysis name has been taken.
        f = open(os.path.join(folder, name), 'w')
        f.write("FileList")
        f.close()