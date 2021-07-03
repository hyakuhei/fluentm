from fluentm import Actor, Boundary, Process, Data, DataFlow
from fluentm import report

# fluentTM Classes are scoped by name, so, I can only have one Boundary called "Internet"
# Attempting to instantiate another with the same name will give you the first one you instantiated
# However, if, for reasons, you wanted to create an Actor called "Internet" and a boundary called "Internet", that's ok. Though it's probably stupid.

Actor("Customer").inBoundary("Internet") # Creates an Actor _and_ a Boundary and Associates them.

# We want to create a big boundary for our bookstore
Boundary("BookStore Co")

# Create a boundary within BookStore Co called "Front End Systems"
Boundary("Front End Systems").inBoundary(Boundary.get("BookStore Co"))
Boundary("Databases").inBoundary(Boundary.get("BookStore Co"))

Boundary("Visa").inBoundary("Internet")

# Create a process for managing web traffic
Process("Web Server").inBoundary(Boundary.get("Front End Systems"))
Process("Content DB").inBoundary(Boundary.get("Databases"))
Process("Stock DB").inBoundary(Boundary.get("Databases"))

# Customer views a book online
customer = Actor.get("Customer")
webserver = Process.get("Web Server")
contentDb = Process.get("Content DB")
stockDb = Process.get("Stock DB")

scenes = {
    # Example using variables, which is fine for small things but gets hard with longer flows
    "Customer views book online":[ 
        DataFlow(customer, webserver, "View item ID"), # Would be nice to describe paramaterized data and transport here easily (Maybe can be inferred by the catcher?)
        DataFlow(webserver, contentDb, "Fetch content for ID"),
        DataFlow(contentDb, webserver, "Image Content, Description"),
        DataFlow(webserver, stockDb, "Get Stock Level"),
        DataFlow(stockDb, webserver, "Stock Level"),
        DataFlow(webserver, customer, "Rendered Item Information") 
    ],
    # Example using .get for registered types (rather than variables), these were all created above
    "Customer buys book":[ 
        DataFlow(Actor.get("Customer"), Process.get("Web Server"), "Buy Item ID"),
        DataFlow(Process.get("Web Server"), Process("Merchant API").inBoundary(Boundary.get("Visa")), "Process payment"), # Dynamic creation of merchant in this flow - not modelled above.
        DataFlow(Process.get("Merchant API"), Process.get("Web Server"), "Confirmation"),
        DataFlow(Process.get("Web Server"), Actor.get("Customer"), "SOLD!")
    ],
    # Example using completely new objects created only here, inline
    "Warehouse packages order":[ 
        DataFlow(
            Process("Order Resolver").inBoundary(Boundary("Logistics")),
            Process("Label Printer").inBoundary(Boundary("Warehouse")),
            "Print label"
            ),
        DataFlow(
            Process.get("Label Printer"),
            Process.get("Order Resolver"),
            "Label ID"
            ),
        DataFlow(
            Process.get("Order Resolver"),
            Process("Warehouse Notifier").inBoundary(Boundary.get("Warehouse")),
            "Pick stock item and use label"
            ),
        DataFlow(
            Process.get("Warehouse Notifier"),
            Process.get("Order Resolver"),
            "Confirmation ID"
            ),
    ] #TODO: Fix silent error on repeat label names
}

if __name__ == "__main__":
    report(scenes, outputDir="testOutput")
