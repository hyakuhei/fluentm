from fluentm import Boundary, Process, DataFlow
from fluentm import dfd, renderDfd

# Example using completely new objects created only here, inline
scenes = {
    "Warehouse packages order":[ 
        DataFlow(
            Process("Order Resolver").inBoundary(Boundary("Logistics")),
            Process("Label Printer").inBoundary(Boundary("Warehouse")),
            "Print label"
            ),
        DataFlow(
            Process.get("Label Printer"),
            Process.get("Order Resolver"),
            "Label ID"
            ),
        DataFlow(
            Process.get("Order Resolver"),
            Process("Warehouse Notifier").inBoundary(Boundary.get("Warehouse")),
            "Pick stock item and use label"
            ),
        DataFlow(
            Process.get("Warehouse Notifier"),
            Process.get("Order Resolver"),
            "Confirmation ID"
            ),
    ] #TODO: Fix silent error on repeat label names
}

expectedResults = {
    "Warehouse packages order":"""digraph "Warehouse packages order" {
	color=blue rankdir=LR
	node [fontname=Arial fontsize=14]
	subgraph cluster_Logistics {
		graph [color=red fontname=Arial fontsize=12 label=Logistics line=dotted]
		"Order Resolver"
	}
	subgraph cluster_Warehouse {
		graph [color=red fontname=Arial fontsize=12 label=Warehouse line=dotted]
		"Label Printer"
		"Warehouse Notifier"
	}
	"Order Resolver" -> "Label Printer" [label="(1) Print label"]
	"Label Printer" -> "Order Resolver" [label="(2) Label ID"]
	"Order Resolver" -> "Warehouse Notifier" [label="(3) Pick stock item and use label"]
	"Warehouse Notifier" -> "Order Resolver" [label="(4) Confirmation ID"]
}"""
}

def test_dfd():
    graph = dfd(scenes, "Warehouse packages order")
    #print(graph)
    renderDfd(graph, "Warehouse packages order", outputDir="testOutput")
    assert graph.__str__() == expectedResults["Warehouse packages order"]
