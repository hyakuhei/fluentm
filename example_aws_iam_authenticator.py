from fluentm import (
    Actor,
    Boundary,
    Process,
    DataFlow,
    Exec,
    HTTP,
    SIGV4,
    TLS,
    Unknown,
    SIGV4,
    Stdout,
    Internal,
)
from fluentm import report

scenes = {
    # Example using variables, which is fine for small things but gets hard with longer flows
    "kubectl gets pre-signed URL": [
        DataFlow(
            Process("kubectl").inBoundary("User Machine"),
            Process("aws-cli").inBoundary("User Machine"),
            Exec("Exec aws-cli get-token"),
        ),
        DataFlow(
            Process("aws-cli"),
            Process("aws-cli"),
            Internal("Sign URL using AWS IAM credentials"),
        ),
        DataFlow(
            Process("aws-cli"), Process("kubectl"), Stdout("STS pre-signed URL")
        ),
    ],
    "API traffic": [
        DataFlow(
            Process("kubectl"),
            Process("Kubernetes API").inBoundary(
                Boundary("EKS Cluster").inBoundary("AWS Cloud")
            ),
            TLS(HTTP("pre-signed URL as Bearer Token HTTP Header")),
        ),
        DataFlow(
            Process("Kubernetes API"),
            Process("aws-iam-authenticator").inBoundary("EKS Cluster"),
            TLS(HTTP("TokenReview request with pre-signed URL")),
        ),
        DataFlow(
            Process("aws-iam-authenticator"),
            Process("AWS STS").inBoundary("AWS Cloud"),
            TLS(HTTP(SIGV4("sts:GetCallerIdentity request"))),
            response=TLS(HTTP("sts:GetCallerIdentity response")),
        ),
        DataFlow(
            Process("aws-iam-authenticator"),
            Process("Kubernetes API").inBoundary("EKS Cluster"),
            TLS(HTTP("TokenReview response with username")),
        ),
        DataFlow(
            Process("aws-iam-authenticator"),
            Process("Kubernetes API").inBoundary("EKS Cluster"),
            TLS(HTTP(("Async Watch mapped aws-auth ConfigMap "))),
            #response=TLS(HTTP("Config Map username mappings")),
        ),
    ],
}

if __name__ == "__main__":
    report(scenes, outputDir="examples/aws-iam-authenticator", dfdLabels=True)
