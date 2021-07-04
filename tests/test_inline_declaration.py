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
\tcolor=blue rankdir=LR
\tnode [fontname=Arial fontsize=14]
\tsubgraph cluster_Logistics {
\t\tcolor=red label=Logistics
\t\t"Order Resolver"
\t}
\tsubgraph cluster_Warehouse {
\t\tcolor=red label=Warehouse
\t\t"Label Printer"
\t\t"Warehouse Notifier"
\t}
\t"Order Resolver" -> "Label Printer" [label="(1) Print label"]
\t"Label Printer" -> "Order Resolver" [label="(2) Label ID"]
\t"Order Resolver" -> "Warehouse Notifier" [label="(3) Pick stock item and use label"]
\t"Warehouse Notifier" -> "Order Resolver" [label="(4) Confirmation ID"]
}"""
}

def test_dfd():
    graph = dfd(scenes, "Warehouse packages order")
    #print(graph)
    assert graph.__str__() == expectedResults["Warehouse packages order"]
    renderDfd(graph, "Jordan", outputDir="testOutput")