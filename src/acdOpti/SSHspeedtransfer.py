# -*- coding: utf8 -*-
#
# Copyright 2012 Kyrre Ness Sjøbæk
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

import os
import subprocess

class SSHspeedtransfer(object):
    """
    This class is a wrapper for scp, used for uploading and downloading a file
    faster than what is possible through paramiko
    """
    
    host = None
    username = None

    def __init__(self,host,username):
        self.host = host
        self.username = username
        
    def put(self, localPath, remotePath):
        assert type(self.host) == str
        assert type(self.username) == str
        
        assert os.path.isfile(localPath)
        
        sp = subprocess.Popen(["/usr/bin/scp", localPath, self.username + "@" + self.host + ":" + remotePath])
        sp.wait()
        
        assert sp.returncode == 0
    
    def get(self, remotePath, localPath):
        assert type(self.host) == str
        assert type(self.username) == str
            
        sp = subprocess.Popen(["/usr/bin/scp", self.username + "@" + self.host + ":" + remotePath, localPath])
        sp.wait()
        
        assert sp.returncode == 0
        