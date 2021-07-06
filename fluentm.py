from __future__ import annotations

from enum import Flag, auto
from types import WrapperDescriptorType
from typing import Union
import logging

from graphviz import Digraph
from jinja2 import FileSystemLoader, Environment

SPACES = "   "


class Unset(object):
    pass


class WrappableProtocol(object):
    def __init__(
        self,
        toWrap: Union[Data, WrappableProtocol],
        encrypted: Union[Unset, bool],
        serverAuthenticated: Union[Unset, bool],
        clientAuthenticated: Union[Unset, bool],
        serverCredential: Union[Unset, str, None],
        clientCredential: Union[Unset, str, None],
        version: Union[Unset, str],
    ):
        if isinstance(toWrap, (WrappableProtocol, Data)):
            self.wraps = toWrap
        elif isinstance(toWrap, str):
            self.wraps = Data(toWrap)

        self.encrypted = encrypted
        self.serverAuthenticated = serverAuthenticated
        self.clientAuthenticated = clientAuthenticated
        self.serverCredential = serverCredential
        self.clientCredential = clientCredential
        self.version = version

    def printChain(self, depth=0):
        print(f"{SPACES * depth} {self.__class__.__name__}")
        print(f"{SPACES*depth} Encrypted: {self.encrypted}")
        print(f"{SPACES*depth} serverAuthenticated: {self.serverAuthenticated}")
        print(f"{SPACES*depth} serverAuthenticated: {self.serverAuthenticated}")
        print(f"{SPACES*depth} serverCredential: {self.serverCredential}")
        print(f"{SPACES*depth} clientCredential: {self.clientCredential}")
        print(f"{SPACES*depth} version: {self.version}")
        # ...
        print(f"{SPACES*depth} Wraps:")
        if isinstance(self.wraps, WrappableProtocol):
            self.wraps.printChain(depth=depth + 1)
        else:
            print(f"{SPACES* (depth+1)} {self.wraps}")

    # Recurse through all nested/wraped protocols and return the data that's ultimately wrapped
    def getData(self):
        if isinstance(self.wraps, Data):
            return self.wraps  # Base case
        else:
            return self.wraps.getData()

    # Recurse and generate a single line str for the wrappable
    def flatString(self, depth=0, s=None):
        if s is None:
            s = ""

        if isinstance(self, WrappableProtocol):
            s += f"{self.__class__.__name__}("
            if isinstance(self.wraps, WrappableProtocol):
                return self.wraps.flatString(depth=depth + 1, s=s)
            if isinstance(self.wraps, Data):
                s += f"{self.wraps.name}{')'*(depth+1)}"
                return s
        else:
            assert False, "Bad instance type in WrappableProtocol structure"

    def __str__(self):
        return self.flatString()


class Plaintext(WrappableProtocol):
    def __init__(self, toWrap):
        super().__init__(
            toWrap,
            encrypted=False,
            serverAuthenticated=False,
            clientAuthenticated=False,
            serverCredential=None,  # TODO: Replace with a type? Would that be useful?
            clientCredential=None,
            version=None,
        )


class IPSEC(WrappableProtocol):
    def __init__(self, toWrap):
        super().__init__(
            toWrap,
            encrypted=True,
            serverAuthenticated=True,
            clientAuthenticated=True,
            serverCredential="x509",  # TODO: Replace with a type? Would that be useful?
            clientCredential="x509",
        )


class TLSVPN(WrappableProtocol):
    def __init__(self, toWrap):
        super().__init__(
            toWrap,
            encrytped=True,
            serverAuthenticated=True,
            clientAuthenticated=False,
            serverCredential="x509",  # TODO: Replace with a type? Would that be useful?
            clientCredential=None,
        )


class MTLSVPN(WrappableProtocol):
    def __init__(self, toWrap):
        super().__init__(
            toWrap,
            encrytped=True,
            serverAuthenticated=True,
            clientAuthenticated=True,
            serverCredential="x509",
            clientCredential="x509",
        )


class SQL(WrappableProtocol):
    def __init__(self, toWrap, version="0"):
        super().__init__(
            toWrap,
            encrypted=False,
            serverAuthenticated=False,
            clientAuthenticated=True,
            serverCredential="Username/Password",
            clientCredential=None,
            version=version,
        )


class TLS(WrappableProtocol):
    def __init__(self, toWrap, version="1.2"):
        super().__init__(
            toWrap,
            encrypted=True,
            serverAuthenticated=True,
            clientAuthenticated=False,
            serverCredential="x509",
            clientCredential=None,
            version=version,
        )


class TLS(WrappableProtocol):
    def __init__(self, toWrap, version="1.2"):
        super().__init__(
            toWrap,
            encrypted=True,
            serverAuthenticated=True,
            clientAuthenticated=False,
            serverCredential="x509",
            clientCredential=None,
            version=version,
        )


class SIGV4(WrappableProtocol):
    def __init__(self, toWrap):
        super().__init__(
            toWrap,
            encrypted=False,
            serverAuthenticated=False,
            clientAuthenticated=False,
            serverCredential=None,
            clientCredential="rsa",
            version=None,
        )


class HTTPBasicAuth(WrappableProtocol):
    def __init__(self, toWrap, version="2.0"):
        super().__init__(
            toWrap,
            encrypted=False,
            serverAuthenticated=False,
            clientAuthenticated=True,
            serverCredential="HTTP Basic Auth",
            clientCredential="Username / Password",
            version=version,
        )


class HTTP(WrappableProtocol):
    def __init__(self, toWrap, version="2.0"):
        super().__init__(
            toWrap,
            encrypted=False,
            serverAuthenticated=False,
            clientAuthenticated=False,
            serverCredential=None,
            clientCredential=None,
            version=version,
        )


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
            assert "processesData called without a data object or a string key to a data object"

        if hasattr(self, "processedData"):
            self.processedData.append(theData)
        else:
            self.processedData = [theData]
        return self

    # static / non-instantiated i.e no 'self'
    def get(className, instanceName):
        assert className in Asset._instances

        if instanceName in Asset._instances[className]:
            return Asset._instances[className][instanceName]
        else:
            # TODO: Think about what exception to throw here
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
    TOPSECRET = auto()
    # SECRET Exposure restuls in signficant impact to at least one customer
    SECRET = auto()
    # SENSITIVE Embarassing to loose control of this but otherwise unimportant
    SENSITIVE = auto()
    # PUBLIC We'd be happy to publish this in our blogs
    PUBLIC = auto()


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
        self.shape = "Circle"


class Data(Asset):
    def __init__(self, name):
        super().__init__(name)
        self.shape = "Data"
        self.classified = Unset()
        self.encryptedAtRest = Unset()

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

    #
    def __init__(
        self,
        pitcher: Union[Actor, Process],
        catcher: Union[Actor, Process],
        data: Union[str, WrappableProtocol, Data],
        label: Union[str, None] = None,
        credential: Union[Unset, Credential, None] = Unset()
    ):
        assert isinstance(
            pitcher, (Actor, Process)
        ), f"pitcher is incorrect type: {pitcher.__class__.__name__}"  # Check pitcher is a type that can initiate a dataflow
        assert isinstance(
            catcher, (Actor, Process)
        ), f"catcher is incorrect type: {catcher.__class__.__name__}"  # Check catcher is a type that can receive a dataflow

        if isinstance(data, str):
            logging.warning(
                f"DataFlow using 'string' for data. Assuming plaintext wrapping. See https://github.com/hyakuhei/fluentm/blob/main/help.md"
            )
            wrappedData = Plaintext(Data(data))
        elif isinstance(data, Data):
            logging.warning(
                f"DataFlow using 'Data'. Assuming plaintext wrapping. See https://github.com/hyakuhei/fluentm/blob/main/help.md"
            )
            wrappedData = Plaintext(data)
        elif isinstance(data, WrappableProtocol):
            wrappedData = data
        else:
            logging.error(
                "DataFlow called with unrecognized data type, String, WrappableProtocol or Data are all acceptable "
            )

        name = ""
        if label is not None:
            name = label
        else:
            name = wrappedData.getData().name

        if name not in DataFlow._instances:
            self.pitcher = pitcher
            self.catcher = catcher
            self.name = name
            self.wrappedData = wrappedData
            DataFlow._instances[name] = self
        else:
            self = DataFlow._instances[name]

    def __repr__(self):
        return f"{self.__class__.__name__}:{self.name}"


def renderDfd(graph: Digraph, title: str, outputDir: str):
    graph.render(f"{outputDir}/{title}-dfd", format="png", view=False)
    print(graph)
    return f"{title}-dfd.png"


def dfd(scenes: dict, title: str, dfdLabels=True, render=False):
    graph = Digraph(title)
    graph.attr(rankdir="LR", color="blue")
    graph.attr("node", fontname="Arial", fontsize="14")

    # Go through the dataflows, create graphs (where there's boundaries) and nodes
    for flow in scenes[title]:
        for e in (flow.pitcher, flow.catcher):
            if hasattr(e, "boundary"):
                if not hasattr(e.boundary, "_cluster"):
                    e.boundary._cluster = Digraph(f"cluster_{e.boundary.name}")
                    e.boundary._cluster.attr(color="red", label=e.boundary.name)

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
            graph.edge(
                flow.pitcher.name,
                flow.catcher.name,
                label=f"({flowcounter}) {flow.name}",
            )
        else:
            graph.edge(flow.pitcher.name, flow.catcher.name, label=f"({flowcounter})")
        flowcounter += 1

    return graph


def dataFlowTable(scenes: dict, key: str):
    table = []
    flowCounter = 1
    for f in scenes[key]:
        table.append(
            {
                "Flow ID": flowCounter,
                "Pitcher": f.pitcher.name,
                "Catcher": f.catcher.name,
                "Data Flow": f.wrappedData.flatString(),
            }
        )
        flowCounter += 1
    return table

def report(scenes: dict, outputDir: str, select=None, dfdLabels=True):
    if select is None:
        select = scenes.keys()

    sceneReports = {}

    for key in select:
        graph = dfd(scenes, key, dfdLabels=dfdLabels)
        sceneReports[key] = {
            "graph": graph,
            "dfdImage": renderDfd(graph, key, outputDir=outputDir),
            "dataFlowTable": dataFlowTable(scenes, key),
        }

    templateLoader = FileSystemLoader(searchpath="./")
    templateEnv = Environment(loader=templateLoader)
    template = templateEnv.get_template("reportTemplate.html")

    with open(f"{outputDir}/ThreatModel.html", "w") as f:
        f.write(
            template.render({"title": "Threat Models", "sceneReports": sceneReports})
        )
