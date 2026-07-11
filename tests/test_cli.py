from pathlib import Path

from typer.testing import CliRunner

from auditai.cli import app

FIXTURES = Path(__file__).parent / "fixtures"
runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.1" in result.stdout


def test_dry_run():
    result = runner.invoke(
        app,
        ["run", "--config", str(FIXTURES / "sample.yml"), "--dry-run"],
    )
    assert result.exit_code == 0
    assert "dry-run OK" in result.output


def test_validate_mock():
    result = runner.invoke(app, ["validate", "--config", str(FIXTURES / "sample.yml")])
    assert result.exit_code == 0
    assert "valid" in result.output
