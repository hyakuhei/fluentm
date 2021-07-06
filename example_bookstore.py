from fluentm import Actor, Boundary, Process, DataFlow, TLS, HTTP, SQL
from fluentm import report

scenes={
        "Customer Login":[
            DataFlow(
                Actor("Customer"),
                Process("Nginx").inBoundary(Boundary("Front End")),
                TLS(HTTP("GET /Login credentials"))),
            DataFlow(
                Process.get("Nginx"),
                Process("User Database").inBoundary(Boundary("Back End")),
                SQL("SELECT user password")
                ),
            DataFlow(Process.get("User Database"), Process.get("Nginx"), SQL("password")),
            DataFlow(Process.get("Nginx"), Actor.get("Customer"), TLS(HTTP("Login Cookie")))
        ],
        "Customer Lists Books":[
            DataFlow(Actor.get("Customer"), Process.get("Nginx"), TLS(HTTP("GET /list, Login Cookie"))),
            DataFlow(Process.get("Nginx"), Process("Stock Database").inBoundary("Back End"), SQL("SELECT stock")),
            DataFlow(Process.get("Stock Database"), Process.get("Nginx"), SQL("Stock Items, Pagination token")),
            DataFlow(Process.get("Nginx"), Actor.get("Customer"), TLS(HTTP("Page listings")))
        ],
        "Customer Views Details":[
            DataFlow(Actor.get("Customer"), Process.get("Nginx"), TLS(HTTP("GET /item, Login Cookie"))),
            DataFlow(Process.get("Nginx"), Process.get("User Database"), HTTP("Log viewed ID")),
            DataFlow(Process.get("Nginx"), Process.get("Stock Database"), SQL("SELECT ID")),
            DataFlow(Process.get("Stock Database"), Process.get("Nginx"), SQL("Stock details, CDN image links")),
            DataFlow(Process.get("Nginx"), Actor.get("Customer"), HTTP("Page html")),
            DataFlow(Actor.get("Customer"), Process("CDN").inBoundary(Boundary("External CDN")), HTTP("GET images"))
        ]
    }

if __name__ == "__main__":
    r = report(scenes, outputDir="examples/bookstore", dfdLabels=True)




