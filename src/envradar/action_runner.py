from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from .config import load_scan_config
from .models import Location, ScanResult
from .render import render_markdown, render_report, write_docs_markdown, write_env_example
from .scanner import scan_repo

OUTPUT_TOKEN = "ENVRADAR_OUTPUT"


@dataclass(frozen=True)
class ActionOptions:
    workspace: Path
    path: str = "."
    config: str | None = None
    report_format: str = "text"
    report_file: str | None = None
    write_example: str | None = None
    write_docs: str | None = None
    fail_on_findings: bool = False
    summary: bool = True
    annotations: bool = True
    output_file: Path | None = None
    summary_file: Path | None = None


@dataclass(frozen=True)
class Annotation:
    level: str
    title: str
    message: str
    location: Location


@dataclass(frozen=True)
class GeneratedFiles:
    report: Path | None = None
    example: Path | None = None
    docs: Path | None = None
    config: Path | None = None

    def items(self) -> list[tuple[str, Path]]:
        pairs: list[tuple[str, Path]] = []
        if self.report is not None:
            pairs.append(("Report", self.report))
        if self.example is not None:
            pairs.append(("Example", self.example))
        if self.docs is not None:
            pairs.append(("Docs", self.docs))
        if self.config is not None:
            pairs.append(("Config", self.config))
        return pairs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envradar-action",
        description="Run envradar in a GitHub Action context.",
    )
    parser.add_argument("--workspace", default=".", help="Repository workspace root.")
    parser.add_argument("--path", default=".", help="Path inside the workspace to scan.")
    parser.add_argument("--config", default="", help="Optional envradar config path.")
    parser.add_argument(
        "--report-format",
        choices=("text", "markdown", "json"),
        default="text",
        help="Format for console output and optional report files.",
    )
    parser.add_argument("--report-file", default="", help="Optional report file path.")
    parser.add_argument("--write-example", default="", help="Optional .env.example output path.")
    parser.add_argument("--write-docs", default="", help="Optional markdown docs output path.")
    parser.add_argument(
        "--fail-on-findings",
        action="store_true",
        help="Exit with status 1 when strict findings exist.",
    )
    parser.add_argument(
        "--no-summary",
        action="store_true",
        help="Do not write to the GitHub step summary file.",
    )
    parser.add_argument(
        "--no-annotations",
        action="store_true",
        help="Do not emit GitHub annotations.",
    )
    parser.add_argument("--output-file", default="", help="Path to GITHUB_OUTPUT.")
    parser.add_argument("--summary-file", default="", help="Path to GITHUB_STEP_SUMMARY.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    options = ActionOptions(
        workspace=Path(args.workspace).resolve(),
        path=args.path,
        config=blank_to_none(args.config),
        report_format=args.report_format,
        report_file=blank_to_none(args.report_file),
        write_example=blank_to_none(args.write_example),
        write_docs=blank_to_none(args.write_docs),
        fail_on_findings=args.fail_on_findings,
        summary=not args.no_summary,
        annotations=not args.no_annotations,
        output_file=path_or_none(args.output_file),
        summary_file=path_or_none(args.summary_file),
    )
    return run_action(options)


def run_action(options: ActionOptions) -> int:
    scan_root = resolve_path(options.workspace, options.path)
    if not scan_root.exists():
        raise FileNotFoundError(f"Path does not exist: {scan_root}")
    if not scan_root.is_dir():
        raise NotADirectoryError(f"Path must be a directory: {scan_root}")

    config, config_path = load_scan_config(scan_root, options.config)
    result = scan_repo(scan_root, config=config)

    report = render_report(result, options.report_format)
    print(report, end="")

    generated = GeneratedFiles(config=config_path)
    if options.report_file:
        report_path = resolve_output_path(scan_root, options.report_file)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
        generated = GeneratedFiles(
            report=report_path,
            example=generated.example,
            docs=generated.docs,
            config=generated.config,
        )
        print(f"Wrote {report_path}")

    if options.write_example:
        example_path = resolve_output_path(scan_root, options.write_example)
        write_env_example(result, example_path)
        generated = GeneratedFiles(
            report=generated.report,
            example=example_path,
            docs=generated.docs,
            config=generated.config,
        )
        print(f"Wrote {example_path}")

    if options.write_docs:
        docs_path = resolve_output_path(scan_root, options.write_docs)
        write_docs_markdown(result, docs_path)
        generated = GeneratedFiles(
            report=generated.report,
            example=generated.example,
            docs=docs_path,
            config=generated.config,
        )
        print(f"Wrote {docs_path}")

    if options.annotations:
        for annotation in build_annotations(result, fail_on_findings=options.fail_on_findings):
            print(format_annotation(annotation))

    if options.summary and options.summary_file is not None:
        summary_text = build_summary(result, scan_root, generated)
        options.summary_file.parent.mkdir(parents=True, exist_ok=True)
        with options.summary_file.open("a", encoding="utf-8") as handle:
            handle.write(summary_text)

    if options.output_file is not None:
        write_outputs(options.output_file, result, generated)

    if options.fail_on_findings and result.strict_findings:
        print(f"envradar found {result.strict_findings} strict finding(s).", flush=True)
        return 1
    return 0


def blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def path_or_none(value: str | None) -> Path | None:
    cleaned = blank_to_none(value)
    return Path(cleaned) if cleaned else None


def resolve_path(root: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    return candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()


def resolve_output_path(scan_root: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    return candidate.resolve() if candidate.is_absolute() else (scan_root / candidate).resolve()


def build_summary(result: ScanResult, scan_root: Path, generated: GeneratedFiles) -> str:
    lines = [
        "# envradar action report",
        "",
        f"Scanned `{scan_root}`.",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Scanned files | {result.scanned_files} |",
        f"| Required runtime vars | {len(result.required_runtime)} |",
        f"| Documented vars | {len(result.keys_for('documented'))} |",
        f"| Missing from .env.example | {len(result.missing_from_examples)} |",
        f"| Documented but not used | {len(result.unused_in_examples)} |",
        f"| Present locally but not documented | {len(result.local_only)} |",
        f"| Workflow-only secrets or vars | {len(result.workflow_only)} |",
        "",
    ]
    if generated.items():
        lines.append("## Generated files")
        lines.append("")
        for label, path in generated.items():
            lines.append(f"- **{label}:** `{path}`")
        lines.append("")

    lines.extend(
        [
            "## Details",
            "",
            render_markdown(result).rstrip(),
            "",
        ]
    )
    return "\n".join(lines)


def build_annotations(result: ScanResult, fail_on_findings: bool) -> list[Annotation]:
    annotations: list[Annotation] = []
    strict_level = "error" if fail_on_findings else "warning"

    for name in result.missing_from_examples:
        locations = result.all_locations_for(name)
        if not locations:
            continue
        annotations.append(
            Annotation(
                level=strict_level,
                title="envradar missing example",
                message=missing_message(name, locations),
                location=locations[0],
            )
        )

    for name in result.unused_in_examples:
        locations = result.locations_for("documented", name)
        if not locations:
            continue
        annotations.append(
            Annotation(
                level="notice",
                title="envradar stale example",
                message=f"{name} is documented but not used in code or compose files.",
                location=locations[0],
            )
        )

    for name in result.local_only:
        locations = result.locations_for("local", name)
        if not locations:
            continue
        annotations.append(
            Annotation(
                level=strict_level,
                title="envradar undocumented local variable",
                message=f"{name} exists in a local .env file but is missing from documented examples.",
                location=locations[0],
            )
        )

    for name in result.workflow_only:
        locations = result.locations_for("workflow_secrets", name) or result.locations_for("workflow_vars", name)
        if not locations:
            continue
        annotations.append(
            Annotation(
                level="notice",
                title="envradar workflow-only variable",
                message=f"{name} only appears in workflow files. Double-check whether contributors need it documented.",
                location=locations[0],
            )
        )

    return annotations


def missing_message(name: str, locations: list[Location]) -> str:
    if len(locations) == 1:
        return f"{name} is used here but missing from .env.example."
    return f"{name} is used here and {len(locations) - 1} other place(s), but missing from .env.example."


def format_annotation(annotation: Annotation) -> str:
    return (
        f"::{annotation.level} file={escape_property(annotation.location.path)},"
        f"line={annotation.location.line},"
        f"title={escape_property(annotation.title)}::"
        f"{escape_message(annotation.message)}"
    )


def escape_property(value: str) -> str:
    escaped = value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    return escaped.replace(":", "%3A").replace(",", "%2C")


def escape_message(value: str) -> str:
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def write_outputs(path: Path, result: ScanResult, generated: GeneratedFiles) -> None:
    values = {
        "scanned-files": str(result.scanned_files),
        "required-runtime-count": str(len(result.required_runtime)),
        "documented-count": str(len(result.keys_for("documented"))),
        "strict-findings": str(result.strict_findings),
        "missing-count": str(len(result.missing_from_examples)),
        "unused-count": str(len(result.unused_in_examples)),
        "local-only-count": str(len(result.local_only)),
        "workflow-only-count": str(len(result.workflow_only)),
        "has-findings": "true" if result.strict_findings else "false",
        "report-path": str(generated.report or ""),
        "example-path": str(generated.example or ""),
        "docs-path": str(generated.docs or ""),
        "config-path": str(generated.config or ""),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for name, value in values.items():
            handle.write(f"{name}<<{OUTPUT_TOKEN}\n{value}\n{OUTPUT_TOKEN}\n")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
