# Fluent threat modeling

FluenTM provides threat modelling diagrams as code. 

The goal of FluenTM is to allow developers to build meaningful 
threat models with as little effort as possible and for those 
diagrams to be maintainable and version controlled.

Typical security review processes suffer from a few common challenges:
1. Developers hate building diagrams for review.
2. Diagrams are rarely complete before the review, leading to long reviews.
3. Reviews (and diagrams), become irrelevant quickly because they're hard to maintain (see 1.)
4. Reviews (and diagrams) can't be validated easily against reality
5. Review materials aren't machine readable and can't easily be fed into automation

FluenTM is built to fit into a GitOps workflow. The idea is that 
developers commit threat models that describe their infrastructure. 

FluenTM has a series of tenets to govern design decisions:
1. Users should not need to know python, or pythonic principles to use FluenTM

FluenTM is incomplete; there's whole big chunks of functionality missing:
* Folding protocol/data definitions 
* Sequence Diagram Support
* Detection of common security anti-patterns
* Reviewer feedback capture mechanism
* Review linter

## Better Options
[PyTM](https://github.com/izar/pytm) is a pythonic framework for threat modelling, it comes with a rich set of primitives, a reporting framework and a database of known threats.
[Theragile](https://threagile.io) is the open-source toolkit which allows to model an architecture with its assets in an agile declarative fashion as a YAML file

