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


"""
The point of this file is to collect all global statics
settings in one file. Currently this is a hard-coded implementation,
but using a file like "~/.acdOpti" instead is a simple change of implementation.
"""

from AcdOptiExceptions import AcdOptiException_settings_notFound

class AcdOptiSettings:
    def __init__(self):
        pass
    
    def getSetting(self, key):
        """
        Gets a setting by the name "key".
        Raises an AcdOptiException_settings_notFound if key is invalid.
        """
        if key == "hopperUser":
            return "ksjobak"
        elif key == "acdtoolpath":
            return "/opt/acdtool/acdtool"
        else:
            raise AcdOptiException_settings_notFound