from AnalysisInterface import AnalysisInterface
import os

class Dummy(AnalysisInterface):
    """
    Dummy analysis that doesn't actually do anything,
    used for testing the abstract machinery
    """
    
    def __init__(self, folder, name):
        print "Dummy::__init()"
        self.type     = "Dummy"
        self.folder   = folder
        self.instName = name
        
        f = open(os.path.join(folder, name), 'r')
        print "In file: '" + f.read() + "'"
        f.close()
        
        self.lockdown = False
    
    @staticmethod
    def createNew(folder,name=None):
        f = open(os.path.join(folder, name), 'w')
        f.write("DummyAna")
        f.close()