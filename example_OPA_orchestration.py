from fluentm import Actor, Boundary, Process, DataFlow, TLS, HTTP, Internal, GIT, SSH
from fluentm import report

# Example of a more code-oriented approach, using variables which will play
# nicely with IDEs. It can be a faster way to write these.

# Setup scenes here:
scenes = {}

newK8sClusterBoundary = Boundary("New Kubernetes Cluster").inBoundary("New AWS Account")

## Developer requests a new cluster
# Participants
developer = Actor("Developer")
clusterOrchestrator = Process("Cluster Orchestrator").inBoundary(
    Boundary("Control Cluster")
)
iam = Process("IAM").inBoundary("AWS")
eks = Process("EKS").inBoundary("AWS")
k8sApi = Process("k8s API").inBoundary(Boundary("New Kubernetes Cluster"))
# Flows
scenes["Developer requests a new cluster"] = [
    DataFlow(developer, clusterOrchestrator, TLS(HTTP("Create cluster request"))),
    DataFlow(clusterOrchestrator, clusterOrchestrator, Internal("Validates user")),
    DataFlow(
        clusterOrchestrator,
        iam,
        TLS(HTTP("Create new account")),
        response=TLS(HTTP("Account Details")),
    ),
    DataFlow(
        clusterOrchestrator,
        eks,
        TLS(HTTP("Create new cluster")),
        response=TLS(HTTP("Cluster Details")),
    ),
    DataFlow(
        clusterOrchestrator, k8sApi, TLS(HTTP("Add default admission controller"))
    ),
]

## Developer creates a pod
# New participants (not seen above)
developer = Actor("Developer")
admissionController = Process("Admission Controller").inBoundary("Cluster Orchestrator")
policyRepo = Process("Policy Repo").inBoundary(Boundary("Version Control"))
opa = Process("OPA")
# DataFlows
scenes["Developer creates a pod"] = [
    DataFlow(developer, k8sApi, TLS(HTTP("Create POD"))),
    DataFlow(k8sApi, admissionController, TLS(HTTP("Validate pod creation"))),
    DataFlow(admissionController, opa, TLS(HTTP("Validate pod creation"))),
    DataFlow(
        opa,
        policyRepo,
        SSH(GIT("Get latest policy")),
        response=SSH(GIT("Latest policy REGO")),
    ),
    DataFlow(opa, k8sApi, TLS(HTTP("Validation Decision"))),
    DataFlow(k8sApi, developer, TLS(HTTP("Approve/Denied"))),
]

if __name__ == "__main__":
    r = report(scenes, outputDir="examples/OPA_orchestration", dfdLabels=True)
