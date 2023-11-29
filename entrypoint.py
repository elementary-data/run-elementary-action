import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from packaging import version
from pydantic import BaseModel

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)


EDR_STAGER_PREFIX = "edr_stager: "


def install_dbt(adapter: str, adapter_version: Optional[str] = None):
    dbt_pkg_name = (
        f"dbt-{adapter}=={adapter_version}" if adapter_version else f"dbt-{adapter}"
    )
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


def install_edr(
    adapter: str, project_dir: Optional[str], profile_target: Optional[str], fail_edr_version: Optional[str]
):
    logging.info("Getting Elementary dbt package version.")
    try:
        dbt_pkg_ver = None

        dbt_command = [
            "dbt",
            "--log-format",
            "json",
            "run-operation",
            "get_elementary_dbt_pkg_version",
            "--project-dir",
            "/edr_stager_dbt_project",
        ]

        if profile_target:
            dbt_command.extend(["--target", profile_target])

        command_results = subprocess.run(
            dbt_command,
            check=True,
            capture_output=True,
            cwd=project_dir,
        ).stdout.decode("utf-8")
        for log_line in command_results.splitlines():
            try:
                log = json.loads(log_line)
            except json.decoder.JSONDecodeError:
                log = {}
            message = log.get("info", {}).get("msg") or log.get("data", {}).get("msg")
            if message and message.startswith(EDR_STAGER_PREFIX):
                dbt_pkg_ver = message[len(EDR_STAGER_PREFIX) :]
                break

    except subprocess.CalledProcessError as err:
        logging.error(f"Failed to get Elementary dbt package version: {vars(err)}")
        raise

    if fail_edr_version and not dbt_pkg_ver:
        dbt_pkg_ver = fail_edr_version
        logging.info(
            f"Elementary version overriden: {dbt_pkg_ver}"
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


def run_edr(edr_command: str, project_dir: Optional[str]):
    logging.info(f"Running the edr command.")
    subprocess.run(edr_command, shell=True, check=True, cwd=project_dir)


class Args(BaseModel):
    adapter: str
    adapter_version: Optional[str]
    project_dir: Optional[str]
    profiles_yml: Optional[str]
    edr_command: str
    bigquery_keyfile: Optional[str]
    gcs_keyfile: Optional[str]
    profile_target: Optional[str]
    fail_edr_version: Optional[str]


def main():
    args = Args(
        adapter=os.getenv("INPUT_WAREHOUSE-TYPE"),
        profiles_yml=os.getenv("INPUT_PROFILES-YML"),
        edr_command=os.getenv("INPUT_EDR-COMMAND"),
        profile_target=os.getenv("INPUT_PROFILE-TARGET") or None,
        project_dir=os.getenv("INPUT_PROJECT-DIR") or None,
        bigquery_keyfile=os.getenv("INPUT_BIGQUERY-KEYFILE") or None,
        gcs_keyfile=os.getenv("INPUT_GCS-KEYFILE") or None,
        adapter_version=os.getenv("INPUT_ADAPTER-VERSION") or None,
        fail_edr_version=os.getenv("INPUT_FAIL-EDR-VERSION") or None,
    )
    install_dbt(args.adapter, args.adapter_version)
    setup_env(args.profiles_yml, args.bigquery_keyfile, args.gcs_keyfile)
    install_edr(args.adapter, args.project_dir, args.profile_target, args.fail_edr_version)
    try:
        run_edr(args.edr_command, args.project_dir)
    except subprocess.CalledProcessError:
        logging.exception(f"Failed to run the edr command.")
        raise


if __name__ == "__main__":
    main()
