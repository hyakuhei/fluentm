from __future__ import annotations
from importlib import resources

from graphviz import Digraph
from jinja2 import PackageLoader, Environment

from fluentm.entities import (
    Boundary,
    DataFlow
)

SPACES = "   "

def renderDfd(graph: Digraph, title: str, outputDir: str):
    graph.render(f"{outputDir}/{title}-dfd", format="png", view=False)
    # print(graph)
    return f"{title}-dfd.png"


def dfd(scenes: dict, title: str, dfdLabels=True, render=False, simplified=False):
    graph = Digraph(title)
    graph.attr(rankdir="LR", color="blue", fontname="Arial")
    graph.attr(
        "node",
        fontname="Arial",
        fontsize="11",
        shape="box",
        style="rounded",
    )
    graph.attr("edge", fontname="Arial", fontsize="11")
    # This will break tests!

    clusterAttr = {
        "fontname": "Arial",
        "fontsize": "11",
        "color": "red",
        "style": "dashed",
    }

    boundaryClusters = {}

    # Track which nodes should be placed in which clusters but place neither until we've built the subgraph structure.
    placements = {}

    # Gather the boundaries and understand how they're nested (but don't nest the graphviz objects ,yet)
    # Graphviz subgraphs can't have nodes added, so you need to populate a graph with nodes first, then subgraph it under another graph
    for flow in scenes[title]:
        for e in (flow.pitcher, flow.catcher):
            if e.name not in placements.keys():
                if hasattr(e, "boundary"):
                    ptr = e
                    while hasattr(ptr, "boundary"):
                        if ptr.boundary.name not in boundaryClusters:
                            boundaryClusters[ptr.boundary.name] = Digraph(
                                name=f"cluster_{ptr.boundary.name}",
                                graph_attr=clusterAttr | {"label": ptr.boundary.name},
                            )
                        ptr = ptr.boundary

                    placements[e.name] = boundaryClusters[e.boundary.name]
                else:
                    placements[e.name] = graph

    # Place nodes in Graphs, ready for subgraphing
    for n in placements:
        placements[n].node(n)

    # Subgraph the nodes
    for c in boundaryClusters:
        b = Boundary(c)  # The boundary name
        if hasattr(b, "boundary"):
            boundaryClusters[b.boundary.name].subgraph(boundaryClusters[c])
        else:
            graph.subgraph(boundaryClusters[c])

    # Add the edges

    if simplified is True:
        edges = (
            {}
        )  # Map the edges and figure out if we need to be double or single ended
        for flow in scenes[title]:
            # This edge is flow.pitcher.name -> flow.catcher.name
            # If we don't have this edge, first check to see if we have it the other way
            if (flow.pitcher.name, flow.catcher.name) not in edges and (
                flow.catcher.name,
                flow.pitcher.name,
            ) not in edges:
                edges[(flow.pitcher.name, flow.catcher.name)] = "forward"
            elif (flow.pitcher.name, flow.catcher.name) not in edges and (
                flow.catcher.name,
                flow.pitcher.name,
            ) in edges:
                edges[(flow.catcher.name, flow.pitcher.name)] = "both"

        for edge in edges:
            graph.edge(edge[0], edge[1], dir=edges[edge])

    else:  # simplified is False
        flowCounter = 1
        for flow in scenes[title]:
            if dfdLabels is True:
                graph.edge(
                    flow.pitcher.name, flow.catcher.name, f"({flowCounter}) {flow.name}"
                )
            else:
                graph.edge(flow.pitcher.name, flow.catcher.name, f"({flowCounter})")
            flowCounter += 1
    return graph


def dataFlowTable(scenes: dict, key: str, images=False, outputDir=""):
    table = []
    flowCounter = 1
    for f in scenes[key]:
        row = {
            "Flow ID": flowCounter,
            "Pitcher": f.pitcher.name,
            "Catcher": f.catcher.name,
            "Transport Chain": f.wrappedData.getTransportChain(),
            "Data": f.wrappedData.getNestedData(),
        }

        if images == True:
            # print(f.wrappedData.flatDotRecordString())
            dfGraph = Digraph(
                filename=f"flow-{_safeFilename(key)}-{flowCounter}",
                directory=outputDir,
                graph_attr={
                    "fontsize": "11",
                    "fontstyle": "Arial",
                    "bgcolor": "transparent",
                },
                node_attr={
                    "fontsize": "11",
                    "fontstyle": "Arial",
                    "shape": "plaintext",
                },
            )
            dfGraph.node(
                name="struct",
                shape="record",
                label=f.wrappedData.flatDotRecordString(),
            )
            dfGraph.render(format="png")

            row["Image Source"] = f"flow-{_safeFilename(key)}-{flowCounter}.png"

        table.append(row)

        flowCounter += 1
    return table


def _mixinResponses(scenes, key):
    newFlows = []
    for f in scenes[key]:
        newFlows.append(f)
        if hasattr(
            f, "response"
        ):  # If there's a response, insert it as a new DataFlow object
            newFlows.append(DataFlow(f.catcher, f.pitcher, f.response))
    scenes[key][:] = newFlows


def _safeFilename(filename):
    return "".join(
        [c for c in filename if c.isalpha() or c.isdigit() or c == " "]
    ).rstrip()


def report(scenes: dict, outputDir: str, select=None, dfdLabels=True):
    if select is None:
        select = scenes.keys()

    for key in scenes.keys():
        _mixinResponses(scenes, key)

    sceneReports = {}
    for key in select:
        graph = dfd(scenes, key, dfdLabels=dfdLabels)

        sceneReports[key] = {
            "graph": graph,
            "dfdImage": renderDfd(graph, key, outputDir=outputDir),
            "dataFlowTable": dataFlowTable(
                scenes, key, images=True, outputDir=outputDir
            ),
        }

    compoundFlows = []
    for flow in scenes.values():
        compoundFlows = compoundFlows + flow

    agg = dfd({"all": compoundFlows}, "all", simplified=True)
    aggDfd = {
        "graph": agg,
        "dfdImage": renderDfd(agg, "AggregatedDfd", outputDir=outputDir),
    }

    loader = PackageLoader("fluentm", "templates")
    env = Environment(loader=loader)
    template = env.get_template("report.html")

    with open(f"{outputDir}/ThreatModel.html", "w") as f:
        f.write(
            template.render(
                {
                    "title": "Threat Models",
                    "sceneReports": sceneReports,
                    "aggregatedDfd": aggDfd,
                }
            )
        )
