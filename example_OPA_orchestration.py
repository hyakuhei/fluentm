from fluentm import Actor, Boundary, Process, DataFlow, TLS, HTTP, Internal, GIT, SSH
from fluentm import report

Process("Policy Repo").inBoundary(Boundary("Version Control"))

Boundary("New Kubernetes Cluster").inBoundary("New AWS Account")

scenes={
        "Developer requests a new cluster":[
            DataFlow(Actor("Developer"), Process("Cluster Orchestrator").inBoundary(Boundary("Control Cluster")), TLS(HTTP("Create cluster request"))),
            DataFlow(Process("Cluster Orchestrator"), Process("Cluster Orchestrator"), Internal("Validates user")),
            DataFlow(Process("Cluster Orchestrator"), Process("IAM").inBoundary("AWS"), TLS(HTTP("Create new account")), response=TLS(HTTP("Account Details"))),
            DataFlow(Process("Cluster Orchestrator"), Process("EKS").inBoundary("AWS"), TLS(HTTP("Create new cluster")), response=TLS(HTTP("Cluster Details"))),
            DataFlow(Process("Cluster Orchestrator"), Process("k8s API").inBoundary(Boundary("New Kubernetes Cluster")), TLS(HTTP("Add default admission controller"))),
        ],
        "Developer creates a pod":[
            DataFlow(Actor("Developer"), Process("k8s API"), TLS(HTTP("Create POD"))),
            DataFlow(Process("k8s API"), Process("Admission Controller").inBoundary("Cluster Orchestrator"), TLS(HTTP("Validate pod creation"))),
            DataFlow(Process("Admission Controller"), Process("OPA").inBoundary("Cluster Orchestrator"), HTTP("Validate pod creation..")),
            DataFlow(Process("OPA"), Process("Policy Repo"), SSH(GIT("Get latest policy")), response=SSH(GIT("Latest policy REGO"))),
            DataFlow(Process("OPA"), Process("k8s API"), TLS(HTTP("Validation Decision"))),
            DataFlow(Process("k8s API"), Actor("Developer"), TLS(HTTP("Approve/Denied")))
        ]
    }

if __name__ == "__main__":
    r = report(scenes, outputDir="examples/OPA_orchestration", dfdLabels=True)




