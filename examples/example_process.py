from fluentm.entities import Actor, Boundary, Process, DataFlow
from fluentm.renderer import report

scenes = {
    "FluenTM": [
        DataFlow(
            Actor("Security"),
            Process("ThreatModel").inBoundary(Boundary("Version Control")),
            "Pull Request: Empty ThreatModel",
        ),
        DataFlow(Actor("Developer"), Process.get("ThreatModel"), "Update threat model"),
        DataFlow(
            Actor.get("Security"),
            Process.get("ThreatModel"),
            "Comments in review tooling",
        ),
        DataFlow(
            Process.get("ThreatModel"),
            Process("Review Meeting"),
            "Security and Dev attend",
        ),
        DataFlow(
            Process.get("Review Meeting"),
            Process.get("ThreatModel"),
            "Updates from meeting",
        ),
    ]
}

if __name__ == "__main__":
    r = report(scenes, outputDir="process", dfdLabels=False)
