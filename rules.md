# Backend II — Web Programming

## 1. Context

The primary objective of this project is to design and develop a robust Python backend solution that integrates advanced AI agent capabilities (via Crew AI). The solution should enable efficient handling of complex tasks by delegating responsibilities to AI agents, while ensuring seamless integration with traditional backend services provided by frameworks such as Django, FastAPI, or command line tools (CLIs).

**Key aspects:**

- **Innovation:** Demonstrate how AI agents can be utilised to improve decision making and automate backend operations.
- **Integration:** Seamlessly combine Crew AI's agent framework with Python-based backend services.
- **Scalability:** Create a solution that can be scaled to support increased data loads and concurrent user requests.

### Goal

The overall goal of the project is to implement an integrated backend system with the following targets:

- **Robustness:** Deliver a dependable solution that reliably processes and responds to API requests.
- **Performance:** Optimise backend performance and response times by using asynchronous processing where appropriate.
- **Extensibility:** Ensure the system is modular and can be extended with additional AI functionalities or services in the future.
- **User Experience:** Provide clear and user-friendly interfaces (e.g. API documentation, CLI tools) that facilitate easy interaction with the backend.

---

## 2. Requirements

To achieve the objective and meet the project goal, the following requirements must be addressed:

### Functional Requirements

**AI Agents Integration:** Utilise Crew AI to manage AI agents responsible for tasks such as data analysis, real-time recommendations, or process automation. Develop clear interfaces for communication between the backend and the AI agents.

**Backend Service Implementation:** Use Python as the primary language. Choose one or more frameworks (Django, FastAPI, or CLI-based solutions) to implement the core backend services. Implement RESTful API endpoints to expose the system's functionalities.

**Data Management:**
- Integrate a reliable database solution (e.g. PostgreSQL, SQLite) for persistent data storage.
- Ensure secure data access and proper management of user sessions/authentication if required.

**Security & Error Handling:** Incorporate proper error handling and logging mechanisms. Implement security best practices (such as input validation, authentication, and authorisation).

### Non-Functional Requirements

**Scalability:** The system should handle increasing loads gracefully with provisions for scaling up services.

**Performance:** Optimise the backend for latency-sensitive operations, particularly where real-time AI decision-making is involved.

**Maintainability:**
- Codebase should follow standard coding conventions (e.g. PEP8).
- Adequate inline comments and external documentation should be provided.

**Testing:**
- Develop unit tests and integration tests to ensure code reliability.
- Incorporate automated testing and Continuous Integration/Continuous Deployment (CI/CD) where possible.

---

## 3. Evaluation (20 points)

Your project will be evaluated based on the quality of what you deliver and how well it meets the objectives. Below is a checklist of everything that must be completed and what we'll be looking for:

### Source Code (3 points)
- Clean, modular, and well-documented Python code.
- Hosted on GitHub/GitLab with a clear structure and meaningful commit messages (following conventional commits).
- A Git tag must be created before the final class session at 23h59 (Lisbon time).
- You must also upload a Github Release Page on Classroom.

### Backend Application (2 points)
- Built with FastAPI, Django, or a CLI-based solution.

### AI Agent Integration (4 points)
- At least one AI agent using Crew AI.
- Clear interface between your backend and the agent(s).
- Agents should perform useful tasks (e.g. analysis, automation, recommendations).

### Database (1 point)
- Persistent data storage using PostgreSQL or SQLite.
- If needed: basic authentication and session handling.

### Documentation (2 points)
- Technical documentation describing:
  - System architecture.
  - Usage.
  - User guide for installation and usage.
- If using FastAPI: auto-generated API docs (e.g. Swagger UI/OpenAPI).
- Brief report summarising:
  - What the project does.
  - Implementation challenges and how you solved them.

### Testing (2 points)
- Unit and integration tests. (minimum of 1 meaningful test per feature)
- Instructions to run tests.

### Deployment (3 points)
- Docker and Docker Compose for containerised deployment.
- CI/CD setup (script or GitHub Actions, etc.)

### Responsible & Transparent Use of AI (3 points)
- Explicit declaration of AI tools used.
- Ability to explain and defend any AI-assisted code; absence of unverified or unexplained AI-generated content.
- Evidence that AI was used as a learning aid rather than as a replacement for understanding.

---

## 4. Plagiarism & AI Misuse

This course adopts a transparency-over-prohibition stance on AI use. AI coding assistants may be used, but the rules below are non-negotiable.

### 4.1 Allowed

- Using AI tools (Claude, GitHub Copilot, Cursor, etc.) to generate, refactor, explain or review code.
- Using AI tools to draft or polish documentation and commit messages.
- Using AI tools to accelerate learning of a framework or library.

### 4.2 Required

- **Declare** every AI tool used in a dedicated "AI Usage" section of the README.md, including: tool name, purpose (for example "Django model boilerplate", "CSS Grid layout help", "debugging help with Docker Compose"), and rough scope.
- **Understand** every line of code you submit. If you cannot explain why a block exists, why it was written that way, or how you would modify it, that code should not be in the project until you do.
- **Defend** your work during the presentation. The tutor may ask any student about any portion of the code. "The AI wrote that" is not a valid answer.

### 4.3 Prohibited

- Submitting AI-generated code, documentation or diagrams without declaration.
- Copying code, assets or text from third-party sources (other students' repositories, tutorials, Stack Overflow answers, etc.) without attribution.

### 4.4 Consequences

- **Undeclared AI use** — automatic forfeit of the Responsible & transparent use of AI criterion (3 pts) and case-by-case review of the affected technical criteria.
- **Inability to defend submitted code** — downward adjustment of the individual score proportional to the scope of the unexplained work.
- **Plagiarism from external sources** — the full project may be invalidated, subject to the school's academic integrity policy.
