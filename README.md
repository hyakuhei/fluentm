# Fluent threat modeling

FluenTM is a tool that enables the creation, validation and maintenance of Threat Models. FluenTM provides a [fluent-style API](https://en.wikipedia.org/wiki/Fluent_interface) to allow engineers to quickly build threat models. 

The goal of FluenTM is go allow engineers to quickly build maintainable threat models. 

FluenTM is built for use by [GitOps](https://www.cloudbees.com/gitops/what-is-gitops) teams, where control systems; configuration and large amounts of documentation are stored in version control. The goal of FluenTM is to allow developers to build meaningful threat models with as little effort as possible and for those diagrams to be maintainable and version controlled.

Typical security review processes suffer from a few common challenges:
1. Developers hate building diagrams for review.
2. Diagrams are rarely complete before the review, leading to long reviews.
3. Reviews (and diagrams), become irrelevant quickly because they're hard to maintain (see 1.)
4. Reviews (and diagrams) can't be validated easily against reality
5. Review materials aren't machine readable and can't easily be fed into automation

FluenTM is built to fit into a GitOps workflow. The idea is that 
developers commit threat models that describe their infrastructure. Security reviewers work
through code review tools to collaborate on the model before the final-review. After the review,
results are captured in the model as a pull request from the security team. The security review
becomes a living, collaboratively maintained document.


![Diagram of process, created with FluenTM](/images/process.png)

The idea is that you can use simplified python, and not even need to understand basic things
like variables, or control structures, but still create a useful diagram.

```python
from fluentm.entities import Actor, Boundary, Process, DataFlow
from fluentm.renderer import report

scenes={
        "FluenTM":[
            DataFlow(
                Actor("Security"),
                Process("ThreatModel").inBoundary(Boundary("Version Control")),
                "Pull Request: Empty ThreatModel"
                ),
            DataFlow(Actor("Developer"), Process.get("ThreatModel"), "Update threat model"),
            DataFlow(Actor.get("Security"), Process.get("ThreatModel"), "Comments in review tooling"),
            DataFlow(Process.get("ThreatModel"), Process("Review Meeting"), "Security and Dev attend"),
            DataFlow(Process.get("Review Meeting"), Process.get("ThreatModel"), "Updates from meeting")
            
        ]
    }

if __name__ == "__main__":
    r = report(scenes, outputDir="examples/process", dfdLabels=False)
```



FluenTM has a series of tenets to govern design decisions:
1. Users should not need to know python, or pythonic principles to use FluenTM

FluenTM is incomplete; there's whole big chunks of functionality missing:
* Sequence Diagram Support
* Detection of common security anti-patterns
* Reviewer feedback capture mechanism
* Review linter

## Alternatives
* [PyTM](https://github.com/izar/pytm) is a pythonic framework for threat modelling, it comes with a rich set of primitives, a reporting framework and a database of known threats.
* [Theragile](https://threagile.io) is the open-source toolkit which allows to model an architecture with its assets in an agile declarative fashion as a YAML file
* [Diagrams](https://github.com/mingrammer/diagrams) generates beautifully balanced architecture digrams

## Installation
```bash
# Install graphviz using apt/brew/yum etc.
echo "Replace this echo command with your installation of graphviz"

# Clone this repo
git clone https://github.com/hyakuhei/fluentm

# CD into the repo
cd fluentm

# Create a virtualenv
python3 -m venv .venv

# Load the virtualenv
source .venv/bin/activate

# Install the requirements
pip install -r requirements.txt

# Generate an example
python3 example_bookstore.py

# Open the example
open examples/bookstore/ThreatModel.html
```
