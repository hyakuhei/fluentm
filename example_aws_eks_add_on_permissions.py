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
            Process("IAM API").inBoundary(Boundary("IAM CP").inBoundary("AWS SVCs")),
            TLS(SIGV4("Create OIDC provider")),
            response=TLS("OIDC URL")
            )
    ],
    "Create an IAM policy & role to allow CPI addon to manage VPC":[
        DataFlow(
            Actor("User"),
            Process("IAM API"),
            TLS(SIGV4("Create Policy")),
            response = TLS("Policy ARN")
        ),
        DataFlow(
            Actor("User"),
            Process("IAM API"),
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
            Process("EKS API").inBoundary(Boundary("EKS CP").inBoundary(Boundary("AWS SVCs"))),
            TLS(SIGV4("Create add-on CNI,\nCluster: $clusterID"))
        ),
        DataFlow(
            Process("EKS API"),
            Process("Kube API"),
            TLS("Create deployment CNI addon\nRole: Role ARN")
        ),
        DataFlow(
            Process("Kube API"),
            Process("aws-iam-authenticator").inBoundary("Kubernetes Control Plane"),
            TLS("Get sts token")
        ),
        DataFlow(
            Process("aws-iam-authenticator"),
            Process("IAM API"),
            TLS("STS Assume Role,\n with web identity"),
            response=TLS("JWT STS Token")
        ),
        DataFlow(
            Process("aws-iam-authenticator"),
            Process("Kube API"),
            TLS("JWT STS Token")
        ),
        DataFlow(
            Process("Kube API"),
            Process("CNI Pod").inBoundary(Boundary("Kubernetes Data Plane").inBoundary("Customer Account")),
            TLS("Launch Pod,\nsvcacct $acct,\nRole ARN,\nJWT STS Token")
        )
    ],
    "CNI configures VPC":[
        DataFlow(
            Process("CNI Pod"),
            Process("VPC API").inBoundary(Boundary("VPC CP").inBoundary(Boundary("AWS SVCs"))),
            TLS("Update VPC configuration,\nSTS token")
        )
    ]
}

if __name__ == "__main__":
    report(scenes, outputDir="examples/aws-eks-add-on-permissions", dfdLabels=True)