# Architecture Discovery Gate — Architect Phase Contract

**Role Model Version: 2.1.0** · **Classification: L1 role boundary**

## Purpose

Architecture Discovery defines the research and decision phase before execution. It is not a new permanent Agent role and does not replace Foreman.

The goal is to prevent high-speed implementation of a poorly chosen direction by requiring appropriate prior-art and landscape analysis before major capability decisions.

## Ownership

Architecture Discovery belongs to **Global Architect / Project Architect**.

Architect owns:

- Prior Art Research;
- Landscape Scan;
- ecosystem and standard analysis;
- Build / Buy / Combine evaluation;
- Architecture Decision Record (ADR);
- route selection and scope boundary.

Foreman does not own strategic exploration. Foreman receives an Architect Decision and executes the resulting Work.

## Flow

```text
Human Goal
    ↓
Architect Discovery
    ↓
Prior Art / Landscape Research
    ↓
Architecture Decision Record
    ↓
Foreman Execution Work
    ↓
Subagents
    ↓
Delivery / Review
```

## Trigger conditions

Architecture Discovery SHOULD be used for:

- new product capabilities;
- new infrastructure systems;
- new technical domains;
- major architecture changes;
- expensive or difficult-to-reverse technical choices.

It is not required for ordinary bug fixes, local refactors, or established patterns with existing decisions.

## Foreman boundary

Foreman MUST verify that an applicable Architect Decision exists before executing architecture-dependent Work.

If execution reveals:

- the decision is invalidated by new evidence;
- acceptance cannot be reached;
- the chosen route creates material risk;
- important prior art was missed;

Foreman submits an Architect Challenge. It does not silently replace the architecture decision with its own strategic research.

## Decision output

A completed Architecture Discovery should produce a durable decision pointer:

```text
architecture_decision:
  status: DECIDED
  record: <ADR pointer>
  route: BUILD | BUY | COMBINE | DEFER
```

The decision record becomes execution input for Foreman; it is not replaced by runtime chat context.
