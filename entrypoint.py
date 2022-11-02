import subprocess
import sys
from pathlib import Path

from packaging import version


def install_dbt(adapter: str):
    dbt_pkg_name = f"dbt-{adapter}"
    print(f"Installing {dbt_pkg_name}")
    subprocess.run([sys.executable, "-m", "pip", "install", dbt_pkg_name], check=True)


def setup_env(profiles_yml: str, bigquery_keyfile: str, gcs_keyfile: str):
    print(f"Setting up the environment.")
    dbt_dir = Path.home() / ".dbt"
    dbt_dir.mkdir(parents=True, exist_ok=True)
    dbt_dir.joinpath("profiles.yml").write_text(profiles_yml)
    Path("/tmp/bigquery_keyfile.json").write_text(bigquery_keyfile)
    Path("/tmp/gcs_keyfile.json").write_text(gcs_keyfile)


def install_edr(adapter: str):
    print("Getting Elementary dbt package version.")
    dbt_pkg_ver = (
        subprocess.run(
            [
                "dbt",
                "-q",
                "run-operation",
                "get_elementary_dbt_pkg_version",
                "--project-dir",
                "/edr_stager_dbt_project",
            ],
            check=True,
            capture_output=True,
        )
        .stdout.decode()
        .strip()
    )
    if not dbt_pkg_ver:
        print("Unable to get Elementary's dbt package version.")
        print(f"Installing latest edr.")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", f"elementary-data[{adapter}]"],
            check=True,
        )
    else:
        dbt_pkg_ver = version.parse(dbt_pkg_ver)
        print(f"Elementary's dbt package version - {dbt_pkg_ver}")
        print(f"Installing latest compatible version with {dbt_pkg_ver}")
        base_compatible_edr_version = version.parse(
            f"{dbt_pkg_ver.major}.{dbt_pkg_ver.minor}.0"
        )
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                f"elementary-data[{adapter}]~={base_compatible_edr_version}",
            ],
            check=True,
        )


def run_edr(edr_command: str):
    subprocess.run(edr_command, shell=True)


def main():
    adapter, profiles_yml, edr_command, bigquery_keyfile, gcs_keyfile = sys.argv
    install_dbt(adapter)
    setup_env(profiles_yml, bigquery_keyfile, gcs_keyfile)
    install_edr(adapter)
    run_edr(edr_command)


if __name__ == "__main__":
    main()
