# Durable Trace Principle

## Purpose

Execution results that affect future recovery must leave durable evidence.

## Must trace

- architecture decisions
- authority changes
- task state transitions
- release decisions
- blocking conditions

## Do not trace

- temporary reasoning
- discarded exploration
- non-authoritative drafts

## Pointer rule

Durable trace creates recoverable references.

Chat is working memory, not SSOT.
