# Hardware Design Rational

## Introduction
This document serves as a technical overview of the hardware design decisions
behind the targeted infrastructure for this project. The focus is on small,
consumer-grade or office-grade PCs. These choices strike a balance between
cost-effectiveness, resource efficiency, and practicality in creating a
functional home lab.

## Goals
- Establish a cost-efficient and resource-conscious home lab.
- Limit blast radius to ensure that failures in the lab do not affect essential home services.
- Create an environment suitable for experimentation and learning.

## Cost Effectiveness
The infrastructure is designed to minimize upfront costs and reduce total cost
of ownership (TCO). Small machines are chosen not only for their affordability
but also for their low energy consumption, which reduces ongoing operational
costs. This design ensures that the lab remains sustainable over time without
unnecessary expense.

## Resource Constraints or Making Problems for Yourself
Operating within defined resource limits allows the lab to simulate real-world
challenges effectively. Overprovisioning hardware can mask configuration
issues, as excess resources may enable poorly configured software to function.
By adhering to realistic constraints, the lab encourages efficient resource
usage and exposes potential problems early.

## Scalability
The infrastructure is scalable, enabling incremental expansion as needs evolve.
Starting small keeps initial costs low while maintaining the ability to grow in
capacity and complexity over time.

## Design Principles
The design emphasizes the following principles:
- **Simplicity:** Keeping configurations straightforward to minimize points of failure.
- **Modularity:** Allowing components to be added or replaced independently.
- **Efficiency:** Prioritizing energy and resource optimization.

### Hardware

NOTE: The current hardware setup was due to choices made several years ago, taking
in account prices on the used and new market, as well as purpose.
The hardware landscape has changed over time.  There's a lot of mini-PCs,
thin clients, etc, and one should do their own research.  One thing to pay
attention to is lease cycles and how this affects the used market.  Another
thing to consider is the cost of ram, storage type, any onboard NICs,
etc, as well as any need for GPUs for LLM experimentation.  Everyone's use
case will differ.

The current setup utilizes HP t730 thin clients, repurposed as servers. These
are chosen for their availability, affordability, and suitability for
virtualization:

- **Cost:** Approximately $100 each on the aftermarket at the time.
- **Upgrades:** Easily expandable to 16GB of RAM (~$35) and 1TB M.2 SSDs (~$60).
- **Power Consumption:** Consumes well under 100W collectively (3 systems + two switches).

Alternative options include micro systems such as Dell Micro Optiplex or Lenovo
ThinkCentre Tiny. While these may offer advantages like smaller size and
rack-mounting capabilities in a 10" rack, they were more expensive when the
lab hardware was purchased.

### Network
The network is designed for simplicity and isolation:
- Two NICs per machine, connected to separate 1Gbps switches.
- VLAN support to segment traffic and maintain isolation.
- Minimal impact on the primary home network, ensuring reliability for
  essential services.

A future improvement could involve adding a dedicated firewall/router to
further isolate the lab from the household network.

## Conclusion
This infrastructure strikes a balance between cost, efficiency, and
scalability, making it ideal for a home lab environment. By adhering to defined
resource constraints and focusing on modular design, the project fosters a
practical and sustainable setup for experimentation and learning.
