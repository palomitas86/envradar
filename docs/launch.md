# Launch notes

## Core pitch

envradar is now both a CLI and a GitHub Action for catching environment-variable drift before it breaks onboarding, CI, or preview deployments.

## Best headline

**Show HN: envradar — a GitHub Action that catches undocumented env vars**

## Alternate headlines

- **Show HN: envradar — stop shipping broken `.env.example` files**
- **envradar — find missing, stale, and workflow-only env vars before merge**
- **I built a GitHub Action that finds env var drift in repos**

## Good first comment

Built this after repeatedly breaking `.env.example` files across projects.

envradar scans code, compose files, local `.env` files, and GitHub Actions workflows to answer a few annoying questions fast:
- what is used in code but undocumented
- what is documented but stale
- what only exists locally or in CI

It can run as a CLI, or as a GitHub Action that leaves annotations and a job summary on pull requests.

Would love feedback on edge cases and monorepo setups.

## Demo workflow snippet

```yaml
- uses: actions/checkout@v5
- uses: CodMughees/envradar@v1
  with:
    fail-on-findings: "true"
```

## Where to post

- Hacker News
- r/programming
- r/devops
- X / Twitter
- GitHub discussions in tooling repos where config drift is painful
