import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from packaging import version
from pydantic import BaseModel

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)


def install_dbt(adapter: str):
    dbt_pkg_name = f"dbt-{adapter}"
    logging.info(f"Installing {dbt_pkg_name}")
    subprocess.run([sys.executable, "-m", "pip", "install", dbt_pkg_name], check=True)


def setup_env(
    profiles_yml: Optional[str],
    bigquery_keyfile: Optional[str],
    gcs_keyfile: Optional[str],
):
    logging.info(f"Setting up the environment.")
    dbt_dir = Path.home() / ".dbt"
    dbt_dir.mkdir(parents=True, exist_ok=True)
    if profiles_yml:
        dbt_dir.joinpath("profiles.yml").write_text(profiles_yml)
    if bigquery_keyfile:
        Path("/tmp/bigquery_keyfile.json").write_text(bigquery_keyfile)
    if gcs_keyfile:
        Path("/tmp/gcs_keyfile.json").write_text(gcs_keyfile)


def install_edr(adapter: str):
    logging.info("Getting Elementary dbt package version.")
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
        logging.info(
            "Unable to get Elementary's dbt package version. Installing latest edr."
        )
        subprocess.run(
            [sys.executable, "-m", "pip", "install", f"elementary-data[{adapter}]"],
            check=True,
        )
    else:
        dbt_pkg_ver = version.parse(dbt_pkg_ver)
        logging.info(
            f"Elementary's dbt package version - {dbt_pkg_ver}. Installing latest compatible version."
        )
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
    logging.info(f"Running the edr command.")
    subprocess.run(edr_command, shell=True, check=True)


class Args(BaseModel):
    adapter: str
    profiles_yml: Optional[str]
    edr_command: str
    bigquery_keyfile: Optional[str]
    gcs_keyfile: Optional[str]


def main():
    args = Args(
        adapter=os.getenv("INPUT_WAREHOUSE-TYPE"),
        profiles_yml=os.getenv("INPUT_PROFILES-YML"),
        edr_command=os.getenv("INPUT_EDR-COMMAND"),
        bigquery_keyfile=os.getenv("INPUT_BIGQUERY-KEYFILE"),
        gcs_keyfile=os.getenv("INPUT_GCS-KEYFILE"),
    )
    install_dbt(args.adapter)
    setup_env(args.profiles_yml, args.bigquery_keyfile, args.gcs_keyfile)
    install_edr(args.adapter)
    try:
        run_edr(args.edr_command)
    except subprocess.CalledProcessError:
        logging.exception(f"Failed to run the edr command.")
        raise


if __name__ == "__main__":
    main()
