from fluentm import Actor, Boundary, Process, Data, DataFlow
from fluentm import dfd

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
}

expectedResults = {
    "Customer views book online":"""digraph "Customer views book online" {
\tcolor=blue rankdir=LR
\tnode [fontname=Arial fontsize=14]
\tsubgraph cluster_Internet {
\t\tcolor=red label=Internet
\t\tCustomer
\t}
\tsubgraph "cluster_BookStore Co" {
\t\tcolor=red label="BookStore Co"
\t\tsubgraph "cluster_Front End Systems" {
\t\t\tcolor=red label="Front End Systems"
\t\t\t"Web Server"
\t\t}
\t\tsubgraph cluster_Databases {
\t\t\tcolor=red label=Databases
\t\t\t"Content DB"
\t\t\t"Stock DB"
\t\t}
\t}
\tCustomer -> "Web Server" [label="(1) View item ID"]
\t"Web Server" -> "Content DB" [label="(2) Fetch content for ID"]
\t"Content DB" -> "Web Server" [label="(3) Image Content, Description"]
\t"Web Server" -> "Stock DB" [label="(4) Get Stock Level"]
\t"Stock DB" -> "Web Server" [label="(5) Stock Level"]
\t"Web Server" -> Customer [label="(6) Rendered Item Information"]
}""",
    "Customer buys book":"""digraph "Customer buys book" {
\tcolor=blue rankdir=LR
\tnode [fontname=Arial fontsize=14]
\tsubgraph cluster_Internet {
\t\tcolor=red label=Internet
\t\tCustomer
\t}
\tsubgraph "cluster_BookStore Co" {
\t\tcolor=red label="BookStore Co"
\t\tsubgraph "cluster_Front End Systems" {
\t\t\tcolor=red label="Front End Systems"
\t\t\t"Web Server"
\t\t}
\t\tsubgraph cluster_Databases {
\t\t\tcolor=red label=Databases
\t\t\t"Content DB"
\t\t\t"Stock DB"
\t\t}
\t\tsubgraph "cluster_Front End Systems" {
\t\t\tcolor=red label="Front End Systems"
\t\t\t"Web Server"
\t\t}
\t}
\tCustomer -> "Web Server" [label="(1) Buy Item ID"]
\t"Web Server" -> "Merchant API" [label="(2) Process payment"]
\t"Merchant API" -> "Web Server" [label="(3) Confirmation"]
\t"Web Server" -> Customer [label="(4) SOLD!"]
}"""
}

def test_dfd_from_variables():
    graph = dfd(scenes, "Customer views book online")
    assert graph.__str__() == expectedResults["Customer views book online"]

def test_dfd_from_gets():
    graph = dfd(scenes, "Customer buys book")
    assert graph.__str__() == expectedResults["Customer buys book"]
