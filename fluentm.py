from enum import Flag, auto
from typing import Union

from graphviz import Digraph

from jinja2 import FileSystemLoader, Environment

class Asset(object):
    _instances = {}

    def __init__(self, name):
        self.name = name

        if self.__class__.__name__ not in Asset._instances:
            Asset._instances[self.__class__.__name__] = {name: self}
        else:
            Asset._instances[self.__class__.__name__][name] = self

    # Magic str/object function
    def inBoundary(self, boundary):
        if isinstance(boundary, Boundary):
            self.boundary = boundary
        elif isinstance(boundary, str):
            try:
                self.boundary = Boundary.get(boundary)
            except:
                self.boundary = Boundary(boundary)
        else:
            assert False, "Bad type to inBoundary"
        return self

    def addCredential(self, credential):
        assert isinstance(credential, Credential)
        if hasattr(self, "credentials"):
            assert isinstance(self.credentials, list)
            self.credentials.append(credential)
        else:
            self.credentials = [credential]
        return self

    # Magic str/object function
    def processesData(self, data):
        theData = None

        if isinstance(data, str):
            theData = Data(data)
        elif isinstance(data, Data):
            theData = data
        else:
            assert("processesData called without a data object or a string key to a data object")            
        
        if hasattr(self, "processedData"):
            self.processedData.append(theData)
        else:
            self.processedData = [theData]
        return self

    #static / non-instantiated i.e no 'self'
    def get(className, instanceName):
        assert className in Asset._instances

        if instanceName in Asset._instances[className]:
            return Asset._instances[className][instanceName]
        else:
            #TODO: Think about what exception to throw here
            assert False, f"Unable to find {className} of type {instanceName}"
            return None

    def __repr__(self):
        return f"{self.__class__.__name__}:{self.name}"


class Boundary(Asset):
    def __init__(self, name):
        super().__init__(name)
        self.shape = "Dotted Box"        

    def get(name):
        return Asset.get("Boundary", name)

class Lifetime(Flag):
    EPHEMERAL = auto()  # Less than an hour
    SHORT = auto()  # Less than a week
    ANNUAL = auto()  # A year
    BIANNUAL = auto()  # Every two years

class Classification(Flag):
    # Exposure results in complete compromise of at least one customer _or_ significant impact to more than one.
    TOPSECRET = (auto())  
    # SECRET Exposure restuls in signficant impact to at least one customer
    SECRET = auto()  
    # SENSITIVE Embarassing to loose control of this but otherwise unimportant
    SENSITIVE = auto()  
    # PUBLIC We'd be happy to publish this in our blogs
    PUBLIC = auto()  

class UNSET(object):
    pass

class Carrier(object):
    def __init__(self, carries, data=None, credentials=None):
        self.encrypted=UNSET()
        self.serverAuthenitcated=UNSET()
        self.serverAuthorized=UNSET()
        self.clientAuthenticated=UNSET()
        self.clientAuenticated=UNSET()
        self.carries = carries
        self.data = data
        self.credentials = credentials

"""
TLS(HTTP(UserCredential, ))
TLS(HTTP(UserCredential))

VPN(Data(UserCred))

FTP(DATA(), CREDENTIAL)
"""

class Protocol(object):
    def __init__(self, name, wraps):
        pass

class Credential(Asset):
    def __init__(self, name):
        super().__init__(name)
        self.shape = "Key"

    def isPrimaryFactor(self):
        self.primaryFactor = True
        return self

    def isSecondFactor(self):
        self.secondFactor = True
        return self

    def isSymmetric(self):
        self.symmetric = True
        return self

    def isAsymmetric(self):
        self.asymmetric = True
        return self

    def hasLifetime(self, lifetime):
        assert isinstance(lifetime, Lifetime)
        self.lifetime = lifetime        
        return self

    def isRevokable(self):
        self.revokable = True
        return self

    def isShared(self):
        self.shared = True
        return self

    def get(name):
        return Asset.get("Credential", name)

class Container(Asset):
    def __init__(self, name):
        super().__init__(name)

class Data(Asset):
    def __init__(self, name):
        super().__init__(name)
        self.shape = "Data"

    def classified(self, classification):
        assert isinstance(classification, Classification)
        self.classification = classification
        return self

    def isEncryptedAtRest(self):
        self.encryptedAtRest = True
        return self

    def get(name):
        return Asset.get("Data", name)

class Actor(Asset):
    def __init__(self, name):
        super().__init__(name)
        self.shape = "Man"
    
    def get(name):
        return Asset.get("Actor", name)

class Process(Asset):
    def __init__(self, name):
        super().__init__(name)
        self.shape = "Square"
    
    def get(name):
        return Asset.get("Process", name)

# DataFlow is _NOT_ an Asset
class DataFlow(object):
    _instances = {}

    #TODO: Typehints
    def __init__(self, pitcher, catcher, name, data=None, credential=None):
        assert isinstance(pitcher, (Actor, Process)), f"pitcher is incorrect type: {pitcher.__class__.__name__}" # Check pitcher is a type that can initiate a dataflow
        assert isinstance(catcher, (Actor, Process)), f"catcher is incorrect type: {catcher.__class__.__name__}" # Check catcher is a type that can receive a dataflow

        if credential is not None:
            assert isinstance(credential, Credential)

        if data is not None:
            assert isinstance(data, (Data, list)) # Check that data is either a Data type of a list
 
            if isinstance(data, list): # If data is a list, check all the elements are Data
                for d in data:
                    assert isinstance(d, Data)

        if name not in DataFlow._instances:
            self.pitcher = pitcher
            self.catcher = catcher
            self.name = name
            if data != None:
                if isinstance(data, Data):
                    self.data = [data]
                if isinstance(data, list): # validated above
                    self.data = data
            DataFlow._instances[name] = self
        else:
            self = DataFlow._instances[name] 

    #def __repr__(self):
    #    return f"{self.__class__.__name__}:{self.name}"

def renderDfd(graph:Digraph, title:str, outputDir:str):
    graph.render(f'{outputDir}/{title}-dfd', format='png', view=False)
    print(graph)
    return f"{title}-dfd.png"

def dfd(scenes:dict, title:str, dfdLabels=True, render=False):
    graph = Digraph(title)
    graph.attr(rankdir='LR', color="blue")
    graph.attr('node', fontname='Arial', fontsize='14')
    
    # Go through the dataflows, create graphs (where there's boundaries) and nodes
    for flow in scenes[title]:
        for e in (flow.pitcher, flow.catcher):  
            if hasattr(e, "boundary"):
                if not hasattr(e.boundary, "_cluster"):
                    e.boundary._cluster = Digraph(f"cluster_{e.boundary.name}")
                    e.boundary._cluster.attr(color='red',label=e.boundary.name)
                
                if not hasattr(e, "_node"):
                    e._node = e.boundary._cluster.node(e.name)
            else:
                if not hasattr(e, "_node"):
                    print(f"Added graph node {e.name}")
                    e._node = graph.node(e.name)
    
    # Gather up the boundaries and look for a subgraph 
    baseBoundaries = []
    for flow in scenes[title]:
        for e in (flow.pitcher, flow.catcher):
            if hasattr(e, "boundary"):
                if e.boundary not in baseBoundaries:
                    baseBoundaries.append(e.boundary)
    
    for b in baseBoundaries:
        # See if this boundary has a parent boundary
        if hasattr(b, "boundary"):
            # it does! ok, lets see if the parent already has a graph structure:
            parent = b.boundary
            if hasattr(parent, "_cluster"):
                parent._cluster.subgraph(b._cluster)
            else:
                print(f"Setting up digraph for {parent} || {parent.name}")
                parent._cluster = Digraph(f"cluster_{parent.name}")
                parent._cluster.attr(label=parent.name, color="red")
                parent._cluster.subgraph(b._cluster)
            
            if parent not in baseBoundaries:
                baseBoundaries.append(parent)
        else:
            graph.subgraph(b._cluster)
    
    flowcounter = 1
    for flow in scenes[title]:
        if dfdLabels:
            graph.edge(flow.pitcher.name, flow.catcher.name, label=f"({flowcounter}) {flow.name}")
        else:
            graph.edge(flow.pitcher.name, flow.catcher.name, label=f"({flowcounter})")
        flowcounter += 1

    return graph

def dataFlowTable(scenes: dict, key: str):
    table = []
    flowCounter = 1
    for f in scenes[key]:
        table.append({
            'Flow ID':flowCounter,
            'Pitcher':f.pitcher.name,
            'Catcher':f.catcher.name,
            'Data Flow':f.name
        })
        flowCounter += 1
    return table

def report(scenes: dict, outputDir: str, select=None, dfdLabels=True):
    if select is None:
        select = scenes.keys()

    sceneReports = {}

    for key in select:
        graph = dfd(scenes, key, dfdLabels=dfdLabels)
        sceneReports[key]={
            'graph': graph,
            'dfdImage': renderDfd(graph, key, outputDir=outputDir),
            'dataFlowTable': dataFlowTable(scenes, key)
        }

    templateLoader = FileSystemLoader(searchpath="./")
    templateEnv = Environment(loader=templateLoader)
    template = templateEnv.get_template("reportTemplate.html")

    with open(f"{outputDir}/ThreatModel.html","w") as f:
        f.write(template.render({'title':"Threat Models", 'sceneReports':sceneReports}))

