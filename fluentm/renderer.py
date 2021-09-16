from __future__ import annotations
from importlib import resources

from graphviz import Digraph
from jinja2 import PackageLoader, Environment

from fluentm.entities import Boundary, DataFlow

SPACES = "   "


def renderDfd(graph: Digraph, title: str, outputDir: str):
    graph.render(f"{outputDir}/{title}-dfd", format="png", view=False)
    # print(graph)
    return f"{title}-dfd.png"


def _addBoundariesToGraph(graph, boundaries):
    pass


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

    clusterAttr = {
        "fontname": "Arial",
        "fontsize": "11",
        "color": "red",
        "style": "dashed",
    }

    assetDrawn = {}
    clusterMap = (
        {}
    )  # Map from a boundary.name to a Digraph, to avoid rebuilding lots of digraphs
    for flow in scenes[title]:
        for asset in (flow.pitcher, flow.catcher):
            if asset.name not in assetDrawn:
                lineage = asset.getBoundaries()
                if len(lineage) == 0:
                    graph.node(asset.name)
                    assetDrawn[asset.name] = True
                else:
                    lineage.reverse()
                    boundaryName = lineage.pop().name
                    if boundaryName not in clusterMap:
                        clusterMap[boundaryName] = Digraph(
                            f"cluster_{boundaryName}",
                            graph_attr=clusterAttr | {"label": boundaryName},
                        )
                    toSub = clusterMap[boundaryName]
                    toSub.node(asset.name)
                    assetDrawn[asset.name] = True

                    while lineage:  # Add all the parents
                        boundaryName = lineage.pop().name
                        if boundaryName not in clusterMap:
                            clusterMap[boundaryName] = Digraph(
                                f"cluster_{boundaryName}",
                                graph_attr=clusterAttr | {"label": boundaryName},
                            )
                        d = clusterMap[boundaryName]
                        d.subgraph(toSub)
                        toSub = d

                    graph.subgraph(
                        toSub
                    )  # Add the grand-grand-grandN parent to the graph

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

    # I'm starting to think I've gone too far with the "Make it easy to write without knowing code" and the BORG
    # Pattern is way more trouble than it's worth in this instance. It's making everything much harder.


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
