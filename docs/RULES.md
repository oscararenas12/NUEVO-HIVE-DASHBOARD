# Development Rules & Practices

## TDD (Test-Driven Development)
- Write the failing test FIRST
- Red -> Green -> Refactor cycle
- No feature code without a failing test
- Both frontend (Vitest) and backend (pytest) follow TDD

## Git Workflow
- Never push directly to main
- Feature branch for every change
- Branch naming: feature/<name>, fix/<name>
- PR required for merge -- human reviews only
- Keep commits small and focused

## PR Process
1. Developer creates feature branch
2. Write code following TDD
3. Agent generates PR description (markdown)
4. Developer copies PR description into GitHub PR
5. Other developer reviews the PR
6. Merge to main after approval
7. CI/CD runs tests automatically

## CI/CD
- PR: run tests for affected service
- Main: run all tests, build Docker images
- Tests must pass before merge

## Plans
- All implementation plans saved to docs/plans/
- Plans written before code -- design first, build second
- Each plan has bite-sized tasks with checkboxes

## Devlog
- Each developer maintains their own devlog
  - Oscar: docs/DEVLOG-OSCAR.md
  - Warrsia: docs/DEVLOG-WARRSIA.md
- Agents write decisions and reasoning after every significant change
- Format: date, who (human/agent), decision, reasoning
- Check devlog after every pull from main / changes from other dev
- This is NOT a changelog -- git tracks what changed. Devlog tracks WHY.

## Code Organization
- Frontend (services/client/) and Backend (services/api/) are separate services
- Each service has its own Dockerfile, tests, and dependencies
- Scraper is independent at root level (paused)
- Keep files small and focused -- one responsibility per file

## User Types
- Admin: owner (Oscar) -- full access
- Employee: regular user (intern/staff) -- scoped access
- Customer: no login -- refund tracking via link only
