from __future__ import annotations

from pathlib import Path

from envradar.action_runner import main


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_action_runner_writes_outputs_and_summary(tmp_path: Path, capsys) -> None:
    repo = tmp_path / "repo"
    write(
        repo / "src/app.py",
        'import os\nDATABASE_URL = os.getenv("DATABASE_URL")\n',
    )
    write(repo / ".env.example", "API_TOKEN=demo\n")

    output_file = tmp_path / "github_output.txt"
    summary_file = tmp_path / "summary.md"
    report_file = repo / "docs/report.md"

    exit_code = main(
        [
            "--workspace",
            str(repo),
            "--path",
            ".",
            "--report-format",
            "markdown",
            "--report-file",
            "docs/report.md",
            "--fail-on-findings",
            "--output-file",
            str(output_file),
            "--summary-file",
            str(summary_file),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "DATABASE_URL" in captured.out
    assert report_file.exists()
    assert "strict-findings" in output_file.read_text(encoding="utf-8")
    assert "# envradar action report" in summary_file.read_text(encoding="utf-8")


def test_action_runner_generates_example_and_docs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write(
        repo / "src/settings.py",
        'import os\nLOG_LEVEL = os.getenv("LOG_LEVEL")\n',
    )
    write(repo / ".env.example", "LOG_LEVEL=info\n")

    exit_code = main(
        [
            "--workspace",
            str(repo),
            "--path",
            ".",
            "--write-example",
            "generated/.env.example",
            "--write-docs",
            "generated/environment.md",
            "--output-file",
            str(tmp_path / "github_output.txt"),
            "--summary-file",
            str(tmp_path / "summary.md"),
            "--no-annotations",
        ]
    )

    assert exit_code == 0
    assert (repo / "generated/.env.example").exists()
    assert (repo / "generated/environment.md").exists()
