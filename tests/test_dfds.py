from fluentm.entities import  Process, DataFlow
from fluentm.renderer import dfd, renderDfd

scenes = {
    "Test ABC": [
        DataFlow(Process("A"), Process("B"), "Edge 1"),
        DataFlow(Process.get("B"), Process("C"), "Edge 2"),
    ],
    "Test DEInOneBoundary": [
        DataFlow(
            Process("D").inBoundary("BOUNDARY"),
            Process("E").inBoundary("BOUNDARY"),
            "Edge 3",
        )
    ],
}

# Be careful with these, they have to be tabs, not spaces
expectedResults = {
    "Test ABC": """digraph "Test ABC" {
	color=blue fontname=Arial rankdir=LR
	node [fontname=Arial fontsize=11 shape=box style=rounded]
	edge [fontname=Arial fontsize=11]
	A
	B
	C
	A -> B [label="(1) Edge 1"]
	B -> C [label="(2) Edge 2"]
}""",
    "Test DEInOneBoundary": """digraph "Test DEInOneBoundary" {
	color=blue fontname=Arial rankdir=LR
	node [fontname=Arial fontsize=11 shape=box style=rounded]
	edge [fontname=Arial fontsize=11]
	subgraph cluster_BOUNDARY {
		graph [color=red fontname=Arial fontsize=11 label=BOUNDARY style=dashed]
		D
		E
	}
	D -> E [label="(1) Edge 3"]
}""",
}


def testABC():
    graph = dfd(scenes, "Test ABC")
    renderDfd(graph, "Test ABC", outputDir="testOutput")
    assert graph.__str__() == expectedResults["Test ABC"]


def testABInOneBoundary():
    graph = dfd(scenes, "Test DEInOneBoundary")
    renderDfd(graph, "Test DEInOneBoundary", outputDir="testOutput")
    assert graph.__str__() == expectedResults["Test DEInOneBoundary"]
