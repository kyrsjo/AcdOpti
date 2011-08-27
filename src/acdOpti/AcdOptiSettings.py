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