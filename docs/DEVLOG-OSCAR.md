# Oscar's Development Log

Format: Date | Who (human/agent) | Decision + Reasoning

---

## 2026-07-28 | Oscar + Claude

### Project foundation and cleanup

Cleaned the repo and established the project structure. Key decisions:

- Switched from Flask to FastAPI: intern studied the FastAPI tutorial extensively, and the project already had FastAPI partially set up. Less migration work.
- Switched from SQLAlchemy to SQLModel: follows the FastAPI tutorial the intern studied. Same ORM underneath, cleaner syntax.
- Chose Shadcn/ui over Chakra UI: more modern, we own the component code, built on Tailwind CSS.
- Kept scraper/ as-is but paused: loader.py has broken imports (references removed app/ modules). Will fix when backend is rebuilt.
- Split repo into services/client (Oscar) and services/api (Warissa) for clear ownership.
- Created docs/ as shared knowledge base with devlogs, rules, and plans.
- All plans must be saved to docs/plans/ before implementation begins.
- Warissa (intern) uses default Claude -- no superpowers skills. Oscar uses Claude with superpowers plugin. Both agents should read docs/ for shared context.
- RULES.md is a draft -- Oscar will refine and add more rules before development begins. Check for updates after every pull.
