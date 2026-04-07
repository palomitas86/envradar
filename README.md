# envradar

Find undocumented, unused, and drifting environment variables before they confuse the next person who clones your repo.

envradar scans source code, `.env` files, Docker Compose files, and GitHub Actions workflows to answer four annoying questions quickly:

- Which variables are used in code but missing from `.env.example`?
- Which variables are documented but no longer used?
- Which variables exist locally but are not documented for new contributors?
- Which secrets only show up in CI pipelines and deserve a second look?

It works both as a CLI and as a reusable GitHub Action.

## Why this is useful

Environment variable drift is one of the most common sources of bad onboarding, broken preview deploys, and “works on my machine” bugs. envradar gives maintainers a low-friction way to catch that drift before publishing a repo or merging a pull request.

## Features

- Detects env vars in Python, JavaScript, TypeScript, Go, Ruby, Java, Kotlin, Rust, PHP, and .NET-style code.
- Parses `.env.example`, `.env.sample`, `.env.template`, and local `.env*` files.
- Detects `${VAR}` placeholders in Docker Compose files.
- Detects `${{ secrets.NAME }}` and `${{ vars.NAME }}` references in GitHub Actions workflows.
- Outputs plain text, markdown, or JSON.
- Supports a small `envradar.yml` config for ignored variables and placeholder values.
- Emits GitHub annotations and a job summary when used as a GitHub Action.
- Exits non-zero in strict mode so you can block merges when drift is found.

## Use as a GitHub Action

After you tag a release such as `v1`, other repositories can use envradar directly:

```yaml
name: envradar
on:
  pull_request:
  push:
    branches: [main]

jobs:
  scan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v5
      - id: envradar
        uses: CodMughees/envradar@v1
        with:
          fail-on-findings: "true"
          report-format: markdown
          report-file: docs/envradar-report.md
      - name: Print summary counts
        run: |
          echo "strict findings: ${{ steps.envradar.outputs.strict-findings }}"
          echo "missing vars:    ${{ steps.envradar.outputs.missing-count }}"
```

What the action gives you:

- workflow annotations pinned to specific files and lines
- a job summary with counts and a markdown report
- optional generated files such as `.env.example` and contributor docs
- outputs you can reuse in later workflow steps

### Action inputs

| Input | Default | Description |
| --- | --- | --- |
| `path` | `.` | Path inside the checked-out repository to scan |
| `config` | empty | Optional path to `envradar.yml` or `.envradar.yml` |
| `report-format` | `text` | Log and file output format: `text`, `markdown`, or `json` |
| `report-file` | empty | Optional path where a report file should be written |
| `write-example` | empty | Optional path where a generated `.env.example` should be written |
| `write-docs` | empty | Optional path where markdown docs should be written |
| `fail-on-findings` | `false` | Fail the workflow when strict findings exist |
| `summary` | `true` | Write a markdown report to the GitHub job summary |
| `annotations` | `true` | Emit GitHub annotations |
| `python-version` | `3.11` | Python version used by the action |

### Action outputs

| Output | Description |
| --- | --- |
| `scanned-files` | Number of files scanned |
| `required-runtime-count` | Runtime variables detected in code and compose files |
| `documented-count` | Variables detected in example/template files |
| `strict-findings` | Total count of missing, stale, and local-only findings |
| `missing-count` | Variables used but missing from documented examples |
| `unused-count` | Documented variables that are no longer used |
| `local-only-count` | Local variables that are not documented |
| `workflow-only-count` | Variables that only appear in workflow files |
| `has-findings` | `true` when strict findings exist |
| `report-path` | Absolute path to a generated report file |
| `example-path` | Absolute path to a generated `.env.example` |
| `docs-path` | Absolute path to generated markdown docs |
| `config-path` | Absolute path to the config file that was loaded |

## Install the CLI from source

```bash
python -m pip install -e .
```

Or with `pipx`:

```bash
pipx install .
```

## Quick start

Scan the current repository:

```bash
envradar .
```

Get copy-pasteable markdown output:

```bash
envradar . --format markdown
```

Fail CI when drift is found:

```bash
envradar . --strict
```

Generate a fresh `.env.example`:

```bash
envradar . --write-example .env.example
```

Generate a docs page for contributors:

```bash
envradar . --write-docs docs/environment.md
```

## Example output

```text
$ envradar .

envradar scanned 42 files.
Required runtime vars: 3
Documented vars: 2

Missing from .env.example (1)
  - DATABASE_URL -- src/settings.py:12, docker-compose.yml:8

Documented but not used (1)
  - SENTRY_DSN -- .env.example:7

Present locally but not documented (1)
  - STRIPE_WEBHOOK_SECRET -- .env:4

Workflow-only secrets or vars (1)
  - PYPI_API_TOKEN -- .github/workflows/release.yml:22
```

## Config

If `envradar.yml` or `.envradar.yml` exists at the repo root, envradar will load it automatically.

```yaml
ignore:
  - CI
  - GITHUB_TOKEN
  - PYPI_API_TOKEN

placeholders:
  DATABASE_URL: postgresql://localhost:5432/app
  REDIS_URL: redis://localhost:6379/0
```

`ignore` removes noisy variables from every report. `placeholders` are used when generating `.env.example`.

## JSON output

```bash
envradar . --format json
```

This is useful for automation, bots, or dashboards.

## CLI in GitHub Actions

If you want full control instead of using the packaged action, you can still install and run the CLI in a workflow:

```yaml
name: envradar-cli
on:
  pull_request:
  push:
    branches: [main]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: python -m pip install -e .
      - run: envradar . --strict
```

## Safety notes

- envradar never prints values from local `.env` files.
- Generated `.env.example` files only reuse values already present in example/template files or explicit placeholders from config.
- Real secrets stay local unless you intentionally type them into tracked example files yourself.

## Limitations

- The scanner relies on static patterns, so deeply dynamic env lookups may be missed.
- Monorepos with many independent apps may want separate runs per package.
- Shell scripts are intentionally not parsed yet to avoid too many false positives.

## Development

```bash
python -m pip install -e .[dev]
ruff check .
pytest
```

## Release the GitHub Action

After the action is working in this repository, tag a major release so other repos can depend on a stable ref:

```bash
git tag -a v1 -m "envradar action v1"
git push origin v1
```

You can move the `v1` tag forward for compatible updates, and publish the action to GitHub Marketplace later.

## License

MIT
