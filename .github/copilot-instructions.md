# Project Coding Rules & Guidelines

> **Last Updated:** June 7, 2025  
> **Version:** 1.0  
> **Project:** IR Thermal Monitoring System

---

## 📋 Table of Contents

1. [Code Quality Standards](#code-quality-standards)
2. [Documentation Protocols](#documentation-protocols)
3. [Task Management Rules](#task-management-rules)
4. [Security Compliance Guidelines](#security-compliance-guidelines)
5. [Process Execution Requirements](#process-execution-requirements)
6. [Core Operational Principles](#core-operational-principles)
7. [Design Philosophy Principles](#design-philosophy-principles)
8. [System Extension Guidelines](#system-extension-guidelines)
9. [Quality Assurance Procedures](#quality-assurance-procedures)
10. [Testing & Simulation Rules](#testing--simulation-rules)
11. [Change Tracking & Governance](#change-tracking--governance)

---

## 🔧 Code Quality Standards

- **Error Handling:** All scripts must implement structured error handling with specific failure modes
- **Documentation:** Every function must include a concise, purpose-driven docstring
- **Preconditions:** Scripts must verify preconditions before executing critical or irreversible operations
- **Timeouts:** Long-running operations must implement timeout and cancellation mechanisms
- **File Operations:** File and path operations must verify existence and permissions before granting access

---

## 📖 Documentation Protocols

- **Synchronization:** Documentation must be synchronised with code changes—no outdated references
- **Consistency:** Markdown files must use consistent heading hierarchies and section formats
- **Executable Code:** Code snippets in documentation must be executable, tested, and reflect real use cases
- **Structure:** Each doc must clearly outline: purpose, usage, parameters, and examples
- **Definitions:** Technical terms must be explained inline or linked to a canonical definition

---

## 📊 Task Management Rules

- **Clarity:** Tasks must be clear, specific, and actionable—avoid ambiguity
- **Assignment:** Every task must be assigned a responsible agent, explicitly tagged
- **Decomposition:** Complex tasks must be broken into atomic, trackable subtasks
- **Compatibility:** No task may conflict with or bypass existing validated system behaviour
- **Security Review:** Security-related tasks must undergo mandatory review by a designated reviewer agent
- **Status Updates:** Agents must update task status and outcomes in the shared task file
- **Dependencies:** Dependencies between tasks must be explicitly declared
- **Escalation:** Agents must escalate ambiguous, contradictory, or unscoped tasks for clarification

---

## 🔐 Security Compliance Guidelines

- **Credentials:** Hardcoded credentials are strictly forbidden—use secure storage mechanisms
- **Input Validation:** All inputs must be validated, sanitised, and type-checked before processing
- **Code Injection:** Avoid using `eval`, unsanitised shell calls, or any form of command injection vectors
- **Least Privilege:** File and process operations must follow the principle of least privilege
- **Logging:** All sensitive operations must be logged, excluding sensitive data values
- **Permissions:** Agents must check system-level permissions before accessing protected services or paths

---

## ⚙️ Process Execution Requirements

- **Logging:** Agents must log all actions with appropriate severity (`INFO`, `WARNING`, `ERROR`, etc.)
- **Error Reporting:** Any failed task must include a clear, human-readable error report
- **Resource Management:** Agents must respect system resource limits, especially memory and CPU usage
- **Progress Tracking:** Long-running tasks must expose progress indicators or checkpoints
- **Retry Logic:** Retry logic must include exponential backoff and failure limits

---

## 🎯 Core Operational Principles

- **No Mock Data:** Agents must never use mock, fallback, or synthetic data in production tasks
- **Test-First:** Error handling logic must be designed using test-first principles
- **Evidence-Based:** Agents must always act based on verifiable evidence, not assumptions
- **Validation:** All preconditions must be explicitly validated before any destructive or high-impact operation
- **Traceability:** All decisions must be traceable to logs, data, or configuration files

---

## 🏗️ Design Philosophy Principles

### KISS (Keep It Simple, Stupid)
- Solutions must be straightforward and easy to understand
- Avoid over-engineering or unnecessary abstraction
- Prioritise code readability and maintainability

### YAGNI (You Aren't Gonna Need It)
- Do not add speculative features or future-proofing unless explicitly required
- Focus only on immediate requirements and deliverables
- Minimise code bloat and long-term technical debt

### SOLID Principles

| Principle | Description |
|-----------|-------------|
| **Single Responsibility** | Each module or function should do one thing only |
| **Open-Closed** | Software entities should be open for extension but closed for modification |
| **Liskov Substitution** | Derived classes must be substitutable for their base types |
| **Interface Segregation** | Prefer many specific interfaces over one general-purpose interface |
| **Dependency Inversion** | Depend on abstractions, not concrete implementations |

---

## 🔌 System Extension Guidelines

- **Conformity:** All new agents must conform to existing interface, logging, and task structures
- **Testing:** Utility functions must be unit tested and peer reviewed before shared use
- **Configuration:** All configuration changes must be reflected in the system manifest with version stamps
- **Compatibility:** New features must maintain backward compatibility unless justified and documented
- **Performance:** All changes must include a performance impact assessment

---

## ✅ Quality Assurance Procedures

- **Review Process:** A reviewer agent must review all changes involving security, system config, or agent roles
- **Proofreading:** Documentation must be proofread for clarity, consistency, and technical correctness
- **User Experience:** User-facing output (logs, messages, errors) must be clear, non-technical, and actionable
- **Error Messages:** All error messages should suggest remediation paths or diagnostic steps
- **Rollback Plans:** All major updates must include a rollback plan or safe revert mechanism

---

## 🧪 Testing & Simulation Rules

- **Test Coverage:** All new logic must include unit and integration tests
- **Data Marking:** Simulated or test data must be clearly marked and never promoted to production
- **CI/CD:** All tests must pass in continuous integration pipelines before deployment
- **Coverage Threshold:** Code coverage should exceed defined thresholds (e.g., 85%)
- **Regression Testing:** Regression tests must be defined and executed for all high-impact updates
- **Separate Logging:** Agents must log test outcomes in separate test logs, not production logs

---

## 📝 Change Tracking & Governance

- **Documentation:** All configuration or rule changes must be documented in the system manifest and changelog
- **Recording:** Agents must record the source, timestamp, and rationale when modifying shared assets
- **Versioning:** All updates must increment the internal system version where applicable
- **Rollback Plans:** A rollback or undo plan must be defined for every major change
- **Audit Trails:** Audit trails must be preserved for all task-modifying operations

---

> **Note:** These rules apply to all aspects of the IR Thermal Monitoring System project and must be followed by all agents and contributors.
