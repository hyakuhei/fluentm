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


class Unset(object):
    pass

class WrappableProtocol(object):
    def __init__(
        self,
        toWrap: Union[Data, WrappableProtocol],
        encrypted: Union[Unset, bool],
        signed: Union[Unset, bool],
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
        self.signed = signed
        self.serverAuthenticated = serverAuthenticated
        self.clientAuthenticated = clientAuthenticated
        self.serverCredential = serverCredential
        self.clientCredential = clientCredential
        self.version = version
        self.protocolData = []

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

    # Recurse and generate a single line str for the wrappable
    def flatString(self, depth=0, s=None):
        if s is None:
            s = ""

        if isinstance(self, WrappableProtocol):
            s += f"{self.__class__.__name__}( "
            if isinstance(self.wraps, WrappableProtocol):
                return self.wraps.flatString(depth=depth + 1, s=s)
            if isinstance(self.wraps, Data):
                s += f"{self.wraps.name}{' )'*(depth+1)}"
                return s
        else:
            assert False, "Bad instance type in WrappableProtocol structure"

    def flatDotRecordString(self, s=None):
        # If we are at the start of the sting, we don't need a |
        if s is None:
            s = ""

        s += f"{self.__class__.__name__}"
        if isinstance(self.version, Unset):
            s = s + f"\n+{self.version}"

        if len(self.protocolData) > 0:
            s += "|{"
            s += "|".join(x.__str__() for x in self.protocolData)
            s += "}"

        s += "|"

        if isinstance(self.wraps, WrappableProtocol):
            return self.wraps.flatDotRecordString(s)

        if isinstance(self.wraps, Data):
            s += "{"
            s += f"{self.wraps.name}"
            s += "}"
            return s

    # Recurse and provide a list of objects
    # Example:
    ## TLS(HTTP("MEEP"))
    ## [TLS, HTTP, "MEEP"]
    def getTransportChain(self, l=None):
        if l is None:
            l = []

        l.append(self)
        if isinstance(self.wraps, WrappableProtocol):
            return self.wraps.getTransportChain(l)
        elif isinstance(self.wraps, Data):
            return l
        else:
            assert False, "Reached the unreachable"

    def getNestedData(self, visited=None):
        if visited is None:
            visited = []  # WrappedData objects can feasibly be cyclical, that's bad.

        if self in visited:
            assert False, "Cyclic Wrapped Data"
        else:
            visited.append(self)

        if isinstance(self.wraps, Data):
            return self.wraps
        else:
            return self.wraps.getNestedData(visited)

    def addProtocolData(self, d: Data):
        self.protocolData.append(d)
        return self

    def __str__(self):
        return self.flatString()


class Plaintext(WrappableProtocol):
    def __init__(self, toWrap):
        super().__init__(
            toWrap,
            encrypted=False,
            signed=False,
            serverAuthenticated=False,
            clientAuthenticated=False,
            serverCredential=None,  # TODO: Replace with a type? Would that be useful?
            clientCredential=None,
            version=None,
        )


class DHCP(Plaintext):
    def __init__(self, toWrap):
        super().__init__(toWrap)


class Exec(WrappableProtocol):
    def __init__(self, toWrap):
        super().__init__(
            toWrap,
            encrypted=False,
            signed=False,
            serverAuthenticated=False,
            clientAuthenticated=False,
            serverCredential=None,  # TODO: Replace with a type? Would that be useful?
            clientCredential=None,
            version=None,
        )


class TCP(WrappableProtocol):
    def __init__(self, toWrap):
        super().__init__(
            toWrap,
            encrypted=False,
            signed=False,
            serverAuthenticated=False,
            clientAuthenticated=False,
            serverCredential=None,  # TODO: Replace with a type? Would that be useful?
            clientCredential=None,
            version=None,
        )


class TCPForwarded(WrappableProtocol):
    def __init__(self, toWrap):
        super().__init__(
            toWrap,
            encrypted=False,
            signed=False,
            serverAuthenticated=False,
            clientAuthenticated=False,
            serverCredential=None,  # TODO: Replace with a type? Would that be useful?
            clientCredential=None,
            version=None,
        )


class Stdout(WrappableProtocol):
    def __init__(self, toWrap):
        super().__init__(
            toWrap,
            encrypted=False,
            signed=False,
            serverAuthenticated=False,
            clientAuthenticated=False,
            serverCredential=None,  # TODO: Replace with a type? Would that be useful?
            clientCredential=None,
            version=None,
        )


class Internal(WrappableProtocol):
    def __init__(self, toWrap):
        super().__init__(
            toWrap,
            encrypted=False,
            signed=False,
            serverAuthenticated=False,
            clientAuthenticated=False,
            serverCredential=None,  # TODO: Replace with a type? Would that be useful?
            clientCredential=None,
            version=None,
        )


class Unknown(WrappableProtocol):
    def __init__(self, toWrap):
        super().__init__(
            toWrap,
            encrypted=False,
            signed=False,
            serverAuthenticated=False,
            clientAuthenticated=False,
            serverCredential=None,  # TODO: Replace with a type? Would that be useful?
            clientCredential=None,
            version=None,
        )
        # TODO some flag for the linter


class JWS(WrappableProtocol):
    def __init__(self, toWrap):
        super().__init__(
            toWrap,
            encrypted=False,
            signed=False,
            serverAuthenticated=False,
            clientAuthenticated=False,
            serverCredential=None,  # TODO: Replace with a type? Would that be useful?
            clientCredential=None,
            version=None,
        )
        # TODO some flag for the linter


class IPSEC(WrappableProtocol):
    def __init__(self, toWrap):
        super().__init__(
            toWrap,
            encrypted=True,
            signed=False,
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
            signed=False,
            serverAuthenticated=True,
            clientAuthenticated=False,
            serverCredential="x509",  # TODO: Replace with a type? Would that be useful?
            clientCredential=None,
        )


class MTLS(WrappableProtocol):
    def __init__(self, toWrap):
        super().__init__(
            toWrap,
            encrypted=True,
            version=None,
            signed=False,
            serverAuthenticated=True,
            clientAuthenticated=True,
            serverCredential="x509",
            clientCredential="x509",
        )


class MTLSVPN(WrappableProtocol):
    def __init__(self, toWrap):
        super().__init__(
            toWrap,
            encrypted=True,
            serverAuthenticated=True,
            clientAuthenticated=True,
            serverCredential="x509",
            clientCredential="x509",
        )


class SSH(WrappableProtocol):
    def __init__(self, toWrap):
        super().__init__(
            toWrap,
            encrypted=True,
            signed=True,
            serverAuthenticated=True,
            clientAuthenticated=False,
            serverCredential="ssh-rsa",  # TODO: Replace with a type? Would that be useful?
            clientCredential=None,
            version=2,
        )


class Chime(WrappableProtocol):
    def __init__(self, toWrap):
        super().__init__(
            toWrap,
            encrypted=False,
            signed=False,
            serverAuthenticated=True,
            clientAuthenticated=False,
            serverCredential="Federated App",  # TODO: Replace with a type? Would that be useful?
            clientCredential=None,
            version=None,
        )


class GIT(WrappableProtocol):
    def __init__(self, toWrap):
        super().__init__(
            toWrap,
            encrypted=False,
            signed=False,
            serverAuthenticated=False,
            clientAuthenticated=False,
            serverCredential=None,
            clientCredential=None,
            version=None,
        )


class SQL(WrappableProtocol):
    def __init__(self, toWrap, version="0"):
        super().__init__(
            toWrap,
            encrypted=False,
            signed=False,
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
            signed=False,
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
            signed=False,
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
            signed=True,
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
            signed=False,
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
            signed=False,
            serverAuthenticated=False,
            clientAuthenticated=False,
            serverCredential=None,
            clientCredential=None,
            version=version,
        )


# Implements Borg pattern for each unique asset
class Asset(object):
    _instances = {}

    def __init__(self, name):
        self.name = name

        if self.__class__.__name__ in Asset._instances:  # e.g Boundary
            if (
                self.name in Asset._instances[self.__class__.__name__]
            ):  # eg Boundary.name == "Internet"
                self.__dict__ = Asset._instances[self.__class__.__name__][
                    self.name
                ].__dict__  # Make both Boundary objects of "internet" have the same dict
            else:
                Asset._instances[self.__class__.__name__][self.name] = self
        else:
            Asset._instances[self.__class__.__name__] = {self.name: self}

    # Magic str/object function
    def inBoundary(self, boundary: Union[Boundary, str]):
        if isinstance(boundary, Boundary):
            self.boundary = boundary
        elif isinstance(boundary, str):
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

    def __str__(self):
        return self.name


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
    def __init__(
        self,
        pitcher: Union[Actor, Process],
        catcher: Union[Actor, Process],
        data: Union[str, WrappableProtocol, Data],
        label: Union[str, None] = None,
        credential: Union[Unset, Credential, None] = Unset(),
        response: Union[WrappableProtocol, None] = None,
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
            name = wrappedData.getNestedData().name

        if response != None:
            self.response = response

        self.pitcher = pitcher
        self.catcher = catcher
        self.name = name
        self.wrappedData = wrappedData

    def __repr__(self):
        return f"{self.__class__.__name__}:{self.name}"

