from fluentm.entities import Actor, Boundary, Process, DataFlow, TLS, HTTP, SQL
from fluentm.renderer import report

scenes = {
    "Customer Login": [
        DataFlow(
            Actor("Customer"),
            Process("Nginx").inBoundary(Boundary("Front End")),
            TLS(HTTP("GET /Login credentials")),
        ),
        DataFlow(
            Process("Nginx"),
            Process("User Database").inBoundary(Boundary("Back End")),
            SQL("SELECT user password"),
        ),
        DataFlow(Process("User Database"), Process("Nginx"), SQL("password")),
        DataFlow(Process("Nginx"), Actor("Customer"), TLS(HTTP("Login Cookie"))),
    ],
    "Customer Lists Books": [
        DataFlow(
            Actor("Customer"), Process("Nginx"), TLS(HTTP("GET /list, Login Cookie"))
        ),
        DataFlow(
            Process("Nginx"),
            Process("Stock Database").inBoundary(Boundary("Back End")),
            SQL("SELECT stock"),
        ),
        DataFlow(
            Process("Stock Database"),
            Process("Nginx"),
            SQL("Stock Items, Pagination token"),
        ),
        DataFlow(Process("Nginx"), Actor("Customer"), TLS(HTTP("Page listings"))),
    ],
    "Customer Views Details": [
        DataFlow(
            Actor("Customer"), Process("Nginx"), TLS(HTTP("GET /item, Login Cookie"))
        ),
        DataFlow(Process("Nginx"), Process("User Database"), HTTP("Log viewed ID")),
        DataFlow(Process("Nginx"), Process("Stock Database"), SQL("SELECT ID")),
        DataFlow(
            Process("Stock Database"),
            Process("Nginx"),
            SQL("Stock details, CDN image links"),
        ),
        DataFlow(Process("Nginx"), Actor("Customer"), HTTP("Page html")),
        DataFlow(
            Actor("Customer"),
            Process("CDN").inBoundary(Boundary("External CDN")),
            HTTP("GET images"),
        ),
    ],
}

if __name__ == "__main__":
    r = report(scenes, outputDir="bookstore", dfdLabels=True)
