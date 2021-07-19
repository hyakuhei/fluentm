from fluentm import Actor, Boundary, Process, Data, DataFlow, HTTP, TLS, SQL
from fluentm import report


scenes = {
    # Example using variables, which is fine for small things but gets hard with longer flows
    "Towers":[ 
        DataFlow(
            Process("Alice").inBoundary(Boundary("A Inner").inBoundary(Boundary("A Mid").inBoundary(Boundary("A Outer")))),
            Process("Bob").inBoundary(Boundary("B Inner").inBoundary(Boundary("B Mid").inBoundary(Boundary("B Outer")))),
            TLS("Helo"),
            response=TLS("Hai")
        )
    ],
    "Enter Charlie":[
        DataFlow(
            Process("Charlie").inBoundary(Boundary("B Outer")),
            Process("Alice"),
            TLS("Yo")
        )
    ]
}

if __name__ == "__main__":
    report(scenes, outputDir="examples/nest")
