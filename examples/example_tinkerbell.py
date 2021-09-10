from fluentm.entities import (
    Actor,
    Process,
    DataFlow,
    HTTP,
    MTLS,
    TLS,
    DHCP,
)
from fluentm.renderer import report

scenes = {
    # Example using variables, which is fine for small things but gets hard with longer flows
    "Tink API traffic": [
        DataFlow(
            Actor("tink-cli"),
            Process("Tink API").inBoundary("Tink Control Plane Network"),
            MTLS(HTTP("API request")),
        ),
        DataFlow(
            Process("Machine").inBoundary("On Premise Network"),
            Process("boots").inBoundary("Tink Control Plane Network"),
            DHCP("IP Request"),
        ),
        DataFlow(
            Process("boots").inBoundary("Tink Control Plane Network"),
            Process("Tink API").inBoundary("Tink Control Plane Network"),
            MTLS(HTTP("API request")),
            "Boots queries for IP",
        ),
        DataFlow(
            Process("Machine").inBoundary("On Premise Network"),
            Process("boots").inBoundary("Tink Control Plane Network"),
            DHCP("PXE Location Request"),
        ),
        DataFlow(
            Process("boots").inBoundary("Tink Control Plane Network"),
            Process("Tink API").inBoundary("Tink Control Plane Network"),
            MTLS(HTTP("API request")),
            "Boots queries for PXE OS location",
        ),
        DataFlow(
            Process("Machine").inBoundary("On Premise Network"),
            Process("Nginx").inBoundary("Tink Control Plane Network"),
            HTTP("Boot OS Request"),
        ),
        DataFlow(
            Process("Machine").inBoundary("On Premise Network"),
            Process("Tink API").inBoundary("Tink Control Plane Network"),
            TLS(HTTP("Workflow")),
        ),
        DataFlow(
            Process("Machine").inBoundary("On Premise Network"),
            Process("Container Registry").inBoundary("Tink Control Plane Network"),
            TLS(HTTP("Container Images")),
        ),
        DataFlow(
            Process("Machine").inBoundary("On Premise Network"),
            Process("Hegel").inBoundary("Tink Control Plane Network"),
            TLS(HTTP("Machine metadata")),
            "Metadata request",
        ),
        DataFlow(
            Process("Machine").inBoundary("On Premise Network"),
            Process("Nginx").inBoundary("Tink Control Plane Network"),
            HTTP("Workload OS"),
        ),
    ]
}

if __name__ == "__main__":
    report(scenes, outputDir="tinkerbell", dfdLabels=True)
