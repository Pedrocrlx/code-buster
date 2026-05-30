# Project Rules & Evaluation

## 1. Context

The primary objective is to design and develop a robust Python backend solution that integrates advanced AI agent capabilities via CrewAI. The solution should enable efficient handling of complex tasks by delegating responsibilities to AI agents, while ensuring seamless integration with traditional backend services (Django, FastAPI, or CLI tools).

**Key aspects:**

- **Innovation** — Demonstrate how AI agents can be utilised to improve decision-making and automate backend operations.
- **Integration** — Seamlessly combine CrewAI's agent framework with Python-based backend services.
- **Scalability** — Create a solution that can be scaled to support increased data loads and concurrent user requests.

### Goal

| Target | Description |
|---|---|
| Robustness | Reliably processes and responds to API requests |
| Performance | Optimise response times using asynchronous processing where appropriate |
| Extensibility | Modular system that can be extended with additional AI functionalities |
| User Experience | Clear interfaces (API docs, CLI tools) for easy interaction |

---

## 2. Requirements

### Functional Requirements

**AI Agents Integration**
- Utilise CrewAI to manage AI agents for tasks such as data analysis, real-time recommendations, or process automation.
- Develop clear interfaces for communication between the backend and the AI agents.

**Backend Service Implementation**
- Use Python as the primary language.
- Choose one or more frameworks (Django, FastAPI, or CLI-based) for core backend services.
- Implement RESTful API endpoints to expose the system's functionalities.

**Data Management**
- Integrate a reliable database solution (PostgreSQL or SQLite) for persistent data storage.
- Ensure secure data access and proper management of user sessions/authentication if required.

**Security & Error Handling**
- Incorporate proper error handling and logging mechanisms.
- Implement security best practices (input validation, authentication, authorisation).

### Non-Functional Requirements

**Scalability** — Handle increasing loads gracefully with provisions for scaling up services.

**Performance** — Optimise the backend for latency-sensitive operations, particularly where real-time AI decision-making is involved.

**Maintainability**
- Follow standard coding conventions (PEP8).
- Provide adequate inline comments and external documentation.

**Testing**
- Develop unit tests and integration tests to ensure code reliability.
- Incorporate automated testing and CI/CD where possible.

---

## 3. Evaluation (20 points)

| Criterion | Points | Requirements | Status |
|---|---|---|---|
| Source Code | 3 | Clean, modular, well-documented Python. Hosted on GitHub/GitLab with conventional commits. Git tag before final class at 23h59 Lisbon time. GitHub Release Page on Classroom. | ✅ Code clean and modular. ⚠️ Git tag + GitHub Release still required before submission. |
| Backend Application | 2 | Built with FastAPI, Django, or a CLI-based solution. | ✅ Typer CLI with 6 commands: `setup`, `init`, `db`, `bust`, `save`, `recall`. |
| AI Agent Integration | 4 | At least one CrewAI agent. Clear backend↔agent interface. Agents perform useful tasks (analysis, automation, recommendations). | ✅ Two CrewAI crews (Buster: processor + organizer; Recall: narrator). Clear interface via `run()` functions. Agents process incidents and narrate past solutions. |
| Database | 1 | Persistent storage with PostgreSQL or SQLite. Basic auth/session handling if needed. | ✅ SQLite via `db.database`. Schema with 8 columns. Tag search, fetch, and save implemented. |
| Documentation | 2 | System architecture, usage guide, installation guide. Swagger/OpenAPI if using FastAPI. Brief report on what the project does and implementation challenges. | ✅ README has architecture diagram, quick-start, all commands with examples, and implementation challenges section. |
| Testing | 2 | Unit and integration tests (minimum 1 meaningful test per feature). Instructions to run tests. | ✅ 26 tests across 5 files (DB, parsing, CLI, bust pipeline, recall pipeline). `make test` documented. CI runs tests automatically. |
| Deployment | 3 | Docker and Docker Compose for containerised deployment. CI/CD setup (script or GitHub Actions). | ✅ `compose.yaml` with Ollama service. GitHub Actions CI with lint and test jobs. `buster setup` automates first-time deployment. |
| Responsible & Transparent AI Use | 3 | See section 4. | ✅ `README.md` AI Usage section lists every file created or modified with Claude Code, the tool used, and the scope of use. |

---

## 4. Plagiarism & AI Misuse

This course adopts a **transparency-over-prohibition** stance on AI use.

### 4.1 Allowed

- Using AI tools (Claude, GitHub Copilot, Cursor, etc.) to generate, refactor, explain, or review code.
- Using AI tools to draft or polish documentation and commit messages.
- Using AI tools to accelerate learning of a framework or library.

### 4.2 Required

- **Declare** every AI tool used in a dedicated "AI Usage" section of `README.md`, including: tool name, purpose (e.g. "Django model boilerplate", "debugging help with Docker Compose"), and rough scope.
- **Understand** every line of code you submit. If you cannot explain why a block exists, why it was written that way, or how you would modify it — that code should not be in the project until you do.
- **Defend** your work during the presentation. The tutor may ask any student about any portion of the code. *"The AI wrote that"* is not a valid answer.

### 4.3 Prohibited

- Submitting AI-generated code, documentation, or diagrams without declaration.
- Copying code, assets, or text from third-party sources (other students' repositories, tutorials, Stack Overflow, etc.) without attribution.

### 4.4 Consequences

| Violation | Consequence |
|---|---|
| Undeclared AI use | Automatic forfeit of the Responsible & Transparent AI criterion (3 pts) + case-by-case review of affected technical criteria |
| Inability to defend submitted code | Downward adjustment of individual score proportional to scope of unexplained work |
| Plagiarism from external sources | Full project may be invalidated, subject to the school's academic integrity policy |
