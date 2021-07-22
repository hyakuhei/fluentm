from fluentm import Actor, Boundary, Process, DataFlow, HTTP, SIGV4, TLS, Unknown, SIGV4, JWS, Internal
from fluentm import report


# 1. Create an IAM OIDC provider for your cluster
# 2. Create an IAM role and attach an IAM policy to it with the permissions that your service accounts need
# 2.a. recommend creating separate roles for each unique collection of permissions
# 3. Associate an IAM role with a service account

scenes = {
    "Create an IAM OIDC provider for cluster":[
        DataFlow(
            Actor("User"),
            Process("EKS").inBoundary("AWS SVCs"),
            TLS(SIGV4("Create OIDC endpoint")),
            response="OIDC provider URL"
        ),
        DataFlow(
            Actor("User"),
            Process("IAM").inBoundary("AWS SVCs"),
            TLS(SIGV4("Add OIDC provider,\n OIDC provider URL"))
            )
    ],
    "Create an IAM policy & role to allow CPI addon to manage VPC":[
        DataFlow(
            Actor("User"),
            Process("IAM"),
            TLS(SIGV4("Create Policy")),
            response = TLS("Policy ARN")
        ),
        DataFlow(
            Actor("User"),
            Process("IAM"),
            TLS(SIGV4("Create Role,\nTrusted Entity: Web Identity,\nIdentity Provider: OIDC URL,\nAttach Policy: Policy ARN")),
            response=TLS("Role ARN")
        )
    ],
    "Associate IAM role to a cluster service account":[
        DataFlow(
            Actor("User"),
            Process("Kube API").inBoundary(Boundary("Kubernetes Control Plane").inBoundary(Boundary("Single Tenant VPC"))),
            TLS(SIGV4("Annotate service account $acct with Role ARN"))
        )
    ],
    "Deploy Addon":[
        DataFlow(
            Actor("User"),
            Process("EKS"),
            TLS(SIGV4("Create add-on CNI,\nCluster: $clusterID"))
        ),
        DataFlow(
            Process("EKS"),
            Process("Kube API"),
            TLS("Deployment Spec:  CNI addon\nRole: Role ARN")
        ),
        DataFlow(
            Process("Kube API"),
            Process("eks-pod-identity-webhook").inBoundary(Boundary("Kubernetes Control Plane")),
            TLS("Pod Spec"),
            response=TLS("Mutated Pod Spec,\nAdd projected token to spec")
        ),
        DataFlow(
            Process("Kube API"),
            Process("Kubelet").inBoundary(Boundary("Kubernetes Data Plane").inBoundary(Boundary("Customer Account"))),
            TLS("Launch Pod,\nPod Spec")
        ),
        DataFlow(
            Process("Kubelet"),
            Process("CNI Pod").inBoundary(Boundary("Kubernetes Data Plane")),
            TLS("Launch Pod,\nsvcacct $acct,\nRole ARN,\nJWT STS Token")
        ),
    ],
    "CNI configures VPC":[
        DataFlow(
            Process("CNI Pod"),
            Process("VPC").inBoundary(Boundary("AWS SVCs")),
            TLS("Update VPC configuration,\nSTS token,\nOperates as Role ARN")
        ),
    ]
}

if __name__ == "__main__":
    report(scenes, outputDir="examples/aws-eks-add-on-permissions", dfdLabels=True)