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


#import exceptions

class InfoFrameException(Exception):
    pass

#GeometryCollection
class InfoFrameException_geometryCollection_dontDelete(InfoFrameException):
    pass #Tried to delete a parameter which is in use

#MeshTemplate
class InfoFrameException_meshTemplate_dontDelete(InfoFrameException):
    pass #Tried to delete a parameter which is in use