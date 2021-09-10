from fluentm.entities import Actor, Boundary, Process, Data, DataFlow, HTTP, TLS
from fluentm.renderer import report

# fluentTM Classes are scoped by name, so, I can only have one Boundary called "Internet"
# Attempting to instantiate another with the same name will give you the first one you instantiated
# However, if, for reasons, you wanted to create an Actor called "Internet" and a boundary called "Internet", that's ok. Though it's probably stupid.

Actor("Customer").inBoundary(
    "Internet"
)  # Creates an Actor _and_ a Boundary and Associates them.

# We want to create a big boundary for our Tiagabookstore
Boundary("Tiaga Co")

# Create a boundary within Tiaga Co called "Front End Systems"
Boundary("Front End Systems").inBoundary(Boundary("Tiaga Co"))
Boundary("Databases").inBoundary(Boundary("Tiaga Co"))

Boundary("Visa").inBoundary("Internet")

# Create a process for managing web traffic
Process("Web Server").inBoundary(Boundary("Front End Systems"))
Process("Content DB").inBoundary(Boundary("Databases"))
Process("Stock DB").inBoundary(Boundary("Databases"))

# Customer views a book online
customer = Actor("Customer")
webserver = Process("Web Server")
contentDb = Process("Content DB")
stockDb = Process("Stock DB")

scenes = {
    # Example using variables, which is fine for small things but gets hard with longer flows
    "Customer views book online": [
        DataFlow(
            customer, webserver, "View item ID"
        ),  # Would be nice to describe paramaterized data and transport here easily (Maybe can be inferred by the catcher?)
        DataFlow(webserver, contentDb, "Fetch content for ID"),
        DataFlow(contentDb, webserver, "Image Content, Description"),
        DataFlow(webserver, stockDb, "Get Stock Level"),
        DataFlow(stockDb, webserver, "Stock Level"),
        DataFlow(webserver, customer, "Rendered Item Information"),
    ],
    # Example using Borg pattern for registered types (rather than variables), these were all created above
    "Customer buys book": [
        DataFlow(Actor("Customer"), Process("Web Server"), TLS(HTTP("Buy Item ID"))),
        DataFlow(
            Process("Web Server"),
            Process("Merchant API").inBoundary(Boundary("Visa")),
            "Process payment",
            response=TLS(HTTP("Confirmation")),
        ),  # Dynamic creation of merchant in this flow - not modelled above.
        DataFlow(Process("Web Server"), Actor("Customer"), TLS(HTTP("SOLD!"))),
    ],
    # Example using completely new objects created only here, inline
    "Warehouse packages order": [
        DataFlow(
            Process("Order Resolver").inBoundary(Boundary("Logistics")),
            Process("Label Printer").inBoundary(Boundary("Warehouse")),
            TLS(HTTP("Print label")),
            response=TLS(HTTP("Label ID")),
        ),
        DataFlow(
            Process("Order Resolver"),
            Process("Warehouse Notifier").inBoundary(Boundary("Warehouse")),
            TLS(HTTP("Pick stock item and use label")),
            response=TLS(HTTP("Confirmation ID")),
        ),
    ],  # TODO: Fix silent error on repeat label names
}

if __name__ == "__main__":
    report(scenes, outputDir="tiaga")
