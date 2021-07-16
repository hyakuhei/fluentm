from fluentm import Actor, Boundary, Process, DataFlow, HTTP, SIGV4, TLS, Unknown, SIGV4, JWS, Internal
from fluentm import report

scenes = {
    # Example using variables, which is fine for small things but gets hard with longer flows
    "kubectl gets pre-signed URL":[
        DataFlow(
            Process("kubectl").inBoundary("User Machine"),
            Process("aws-cli").inBoundary("User Machine"),
            Internal("Exec aws-cli get-token")
            ),
        DataFlow(
            Process("aws-cli"),
            Process("AWS IAM").inBoundary("AWS"),
            TLS(HTTP(SIGV4("Get STS Token"))),
            response = TLS(HTTP(JWS("STS Token")))
            )
    ],
    "API traffic": [
        DataFlow(
            Process("kubectl"),
            Process("k8s api").inBoundary("EKS Data Plane").inBoundary("EKS Cluster"),
            TLS(HTTP("STS token in HTTP header")),
        ),
        DataFlow(
            Process("k8s api"),
            Process("aws-iam-authenticator").inBoundary("EKS Data Plane"),
            Unknown("STS Request from token"),
        ),
        DataFlow(
            Process("aws-iam-authenticator"),
            Process("AWS IAM"),
            TLS(HTTP(SIGV4("STS Request"))),
            response=Unknown("?"),
        ),
        DataFlow(
            Process("aws-iam-authenticator"),
            Process("aws-auth").inBoundary("EKS Data Plane"),
            Unknown("Config Map"),
        ),
        DataFlow(
            Process("aws-iam-authenticator"),
            Process("k8s api"),
            Unknown("Mapped username"),
        )
    ]  # TODO: Fix silent error on repeat label names
}

if __name__ == "__main__":
    report(scenes, outputDir="examples/aws-iam-authenticator", dfdLabels=True)