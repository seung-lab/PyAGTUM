from configobj import ConfigObj
import numpy as np

def isnumeric(string):
    try:
        float(string)
        return True

    except ValueError:
        return False       

class config(ConfigObj):  
    def __init__(self,configfile):
        ConfigObj.__init__(self,configfile, encoding="utf-8-sig")

    def LoadConfig(self,obj,SectionName=None):
        if SectionName==None:
            SectionName=obj.__class__.__name__

        if not SectionName in self:
            return 0

        allAttributes=self[SectionName]

        for key in allAttributes:
            if not hasattr(obj,key):
                continue

            attribute=self.Cast(allAttributes[key],getattr(obj,key))
            setattr(obj,key,attribute)
#            print SectionName, key, attribute
        return 1

    

    def Cast(self,attr,template):
        templClass=template.__class__.__name__

        if templClass=='list':
            return list(self.ParseListTupleString(attr))
        elif templClass=='tuple':
            return tuple(self.ParseListTupleString(attr))
        elif templClass=='ndarray':
            return np.array(self.ParseListTupleString(attr),dtype=template.dtype)
        elif templClass=='int':
            return int(float(attr))
        elif templClass=='float':
            return float(attr)
        elif templClass=='bool':           
            return self._bools[attr.lower()]
        elif templClass=='unicode':           
            return str(attr,"utf-8")
        elif templClass=='str':           
            return str(attr)
        else:
            return attr

    def ParseListTupleString(self,string):
        if string.__class__.__name__=="tuple":
            return tuple(self.ParseListTupleString(element) for element in string)
        if string.__class__.__name__=="list":
            return list(self.ParseListTupleString(element) for element in string)
        if (string.startswith(u"[") and string.endswith(u"]")):
            string=string[1:(string.__len__()-1)]
            string=string.split(u",")
            return [self.ParseListTupleString(element) for element in string ]
        elif (string.startswith("[") and string.endswith("]")):
            string=string[1:(string.__len__()-1)]
            string=string.split(",")
            return [self.ParseListTupleString(element) for element in string ]
        elif string.startswith(u"(") and string.endswith(u")"):
            string=string[1:(string.__len__()-1)]
            string=string.split(u",")
            return tuple(self.ParseListTupleString(element) for element in string ) 
        elif string.startswith("(") and string.endswith(")"):
            string=string[1:(string.__len__()-1)]
            string=string.split(",")
            return tuple(self.ParseListTupleString(element) for element in string )            
        else:
            if (string.startswith(u" u''") and string.endswith(u"''")):
                string=string[4:(string.__len__()-2)]
            elif (string.startswith(" u''") and string.endswith("''")):
                string=string[4:(string.__len__()-2)]
            elif (string.startswith(u" ''") and string.endswith(u"''")):
                string=string[3:(string.__len__()-2)]
            elif (string.startswith(" ''") and string.endswith("''")):
                string=string[3:(string.__len__()-2)]
            elif (string.startswith(u"''") and string.endswith(u"''")):
                string=string[2:(string.__len__()-2)]
            elif (string.startswith("''") and string.endswith("''")):
                string=string[2:(string.__len__()-2)]
            elif (string.startswith(u" u'") and string.endswith(u"'")):
                string=string[3:(string.__len__()-1)]
            elif (string.startswith(u" '") and string.endswith(u"'")):
                string=string[2:(string.__len__()-1)]
            elif (string.startswith(" u'") and string.endswith("'")):
                string=string[3:(string.__len__()-1)]
            elif (string.startswith(" '") and string.endswith("'")):
                string=string[2:(string.__len__()-1)]
            if (string.startswith(u' u"') and string.endswith(u'"')):
                string=string[3:(string.__len__()-1)]
            elif (string.startswith(u' "') and string.endswith(u'"')):
                string=string[2:(string.__len__()-1)]
            elif (string.startswith(' u"') and string.endswith('"')):
                string=string[3:(string.__len__()-1)]
            elif (string.startswith(' "') and string.endswith('"')):
                string=string[2:(string.__len__()-1)]
            if (string.startswith(u"u'") and string.endswith(u"'")):
                string=string[2:(string.__len__()-1)]
            elif (string.startswith(u"'") and string.endswith(u"'")):
                string=string[1:(string.__len__()-1)]
            elif (string.startswith("u'") and string.endswith("'")):
                string=string[2:(string.__len__()-1)]
            elif (string.startswith("'") and string.endswith("'")):
                string=string[1:(string.__len__()-1)]
            if (string.startswith(u'u"') and string.endswith(u'"')):
                string=string[2:(string.__len__()-1)]
            elif (string.startswith(u'"') and string.endswith(u'"')):
                string=string[1:(string.__len__()-1)]
            elif (string.startswith('u"') and string.endswith('"')):
                string=string[2:(string.__len__()-1)]
            elif (string.startswith('"') and string.endswith('"')):
                string=string[1:(string.__len__()-1)]
            if string.startswith(u' '):
                string=string[1:string.__len__()]
            elif string.startswith(' '):
                string=string[1:string.__len__()]
            if string.__class__.__name__=="str" or string.__class__.__name__=="unicode":                
                if isnumeric(string):
                    if string.isdigit():
                        string=int(string)
                    else:
                        string=float(string)
                elif u',' in string:
                    string=string.split(u",")
                    return list(self.ParseListTupleString(element) for element in string)
                elif ',' in string:
                    string=string.split(",")
                    return list(self.ParseListTupleString(element) for element in string)
            return string

            

    def SaveConfig(self,obj,SectionName=None):
        attributes2exclude=['_inspec','_original_configspec','_created'] +  dir(config)
        if SectionName==None:
            SectionName=obj.__class__.__name__

        allAttributes=list(set(dir(obj))-set(attributes2exclude))        

        for key in allAttributes:
            if key.__len__()<2:
                continue

            if (not key[0]=="_") or key[1]=="_":
                continue

            attribute=getattr(obj,key)
            if callable(attribute):
                continue

            attr_class=attribute.__class__.__name__
            if attr_class[0]=="Q": #very likely it is a QT GUI object; somewhat dirty hack
                continue

            if not SectionName in self:
                self[SectionName]={}

            if attr_class=="ndarray":
                attribute=[item for item in attribute]

            self[SectionName][key]=attribute
#            print SectionName, key, attribute