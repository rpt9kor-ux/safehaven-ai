# Project Brief: SafeHaven HR & Compliance AI Assistant

## 1. Client Scenario
**Client:** SafeHaven Logistics (fictional), a company with 2,000 employees
across 6 US states.

**Problem:** HR policies, safety regulations, and state-specific
compliance manuals are spread across dozens of long PDFs. HR staff spend
hours each week answering repeat questions, and employees often get
inconsistent answers.

**Goal:** Build an internal AI assistant that answers policy questions
in plain English, always citing the source document and page.

## 2. Users
| Role | Description | Permissions |
|---|---|---|
| Employee | Any staff member | Ask questions, view general HR documents |
| HR Admin | HR team member | Everything an employee can do, plus upload, replace, and delete documents |

## 3. Functional Requirements
- FR-1: Users can register and log in securely.
- FR-2: HR Admins can upload PDF policy documents.
- FR-3: The system extracts, splits, and indexes document text.
- FR-4: Users can ask questions in natural language.
- FR-5: Every answer includes citations (document name and page).
- FR-6: If the answer is not in the documents, the AI says so and does not guess.
- FR-7: Chat history is saved per user.
- FR-8: Documents are tagged by access level (General or HR-Only), and users only see answers from documents they are allowed to access.

## 4. Non-Functional Requirements
- NFR-1: Passwords are hashed and never stored in plain text.
- NFR-2: Secrets are kept in environment variables, never in code.
- NFR-3: The entire system starts with one command (`docker compose up`).
- NFR-4: Automated tests cover core backend logic.
- NFR-5: Answers return in under 10 seconds for typical questions.

## 5. Out of Scope (Version 1)
- Single sign-on (SSO)
- Mobile app
- Languages other than English

## 6. Success Metrics
- At least 90% of test questions answered with a correct citation.
- 0 answers given from documents the user is not allowed to see.