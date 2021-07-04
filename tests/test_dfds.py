from fluentm import Actor, Boundary, Process, Data, DataFlow
from fluentm import dfd

scenes={
        "Test ABC":[
            DataFlow(Process("A"), Process("B"), "Edge 1"),
            DataFlow(Process.get("B"), Process("C"), "Edge 2")
        ],
        "Test ABCInOneBoundary":[ #These aren't using .get, they will replace A, B above... that can't be right...
            DataFlow(Process("A").inBoundary("BOUNDARY"), Process("B").inBoundary("BOUNDARY"), "Edge 3")

        ]
    }

# Be careful with these, they have to be tabs, not spaces
expectedResults={
    "Test ABC":"""digraph "Test ABC" {
\tcolor=blue rankdir=LR
\tnode [fontname=Arial fontsize=14]
\tA
\tB
\tC
\tA -> B [label="(1) Edge 1"]
\tB -> C [label="(2) Edge 2"]
}""",
    "Test ABCInOneBoundary":"""digraph "Test ABCInOneBoundary" {
\tcolor=blue rankdir=LR
\tnode [fontname=Arial fontsize=14]
\tsubgraph cluster_BOUNDARY {
\t\tcolor=red label=BOUNDARY
\t\tA
\t\tB
\t}
\tA -> B [label="(1) Edge 3"]
}"""
}

def testABC():
    graph = dfd(scenes, "Test ABC")
    assert graph.__str__() == expectedResults['Test ABC']

def testABInOneBoundary():
    graph = dfd(scenes, "Test ABCInOneBoundary")
    print(graph)
    assert graph.__str__() == expectedResults['Test ABCInOneBoundary']
    