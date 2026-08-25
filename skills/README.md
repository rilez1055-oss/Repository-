# Skills Policy

Skills are treated as privileged code and instructions.

## Approval checklist

Before a Skill is mounted into a Responses shell environment:

1. Identify the exact Skill name and immutable version.
2. Inspect `SKILL.md` and all bundled files.
3. Review dependencies and executable files.
4. Review network access and external destinations.
5. Identify filesystem/data access and write capabilities.
6. Reject instructions that attempt to exfiltrate secrets, bypass authorization, or weaken repository policy.
7. Require explicit approval for write/high-impact actions.
8. Keep an auditable record of the approved Skill version.
9. Never allow arbitrary end-user selection from an open Skill catalog.

## Authorization rule

A Skill can explain or orchestrate an action, but it cannot authorize that action. MCP/server-side policy must independently evaluate the authenticated principal, action, resource, and current policy at execution time.

## Versioning rule

Pin an approved Skill version for production. Review and approve a new version before promotion. A Skill version change is a behavioral change, not merely a cache refresh.
