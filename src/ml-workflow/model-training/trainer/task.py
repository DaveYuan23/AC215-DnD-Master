# trainer/task.py

import argparse
import yaml
from pathlib import Path

from trainer.gemini_tuner import (
    start_tuning,
    check_status,
    wait_until_complete,
    get_tuned_model_name,
)

# -----------------------------
# Load YAML Config
# -----------------------------
CONFIG_PATH = "/app/configs/training_config.yaml"

with open(CONFIG_PATH, "r") as f:
    cfg = yaml.safe_load(f)

exp_cfg = cfg["experiment"]
proj_cfg = cfg["project"]
model_cfg = cfg["model"]
data_cfg = cfg["data"]
train_cfg = cfg["training"]


# -----------------------------
# Commands
# -----------------------------
def cmd_tune(args):
    # Allow override epochs in CLI
    epochs = args.epochs if args.epochs else train_cfg["epochs"]

    print(f"=== COMMAND: START TUNING (epochs={epochs}) ===")

    job_name = start_tuning(
        project_id=proj_cfg["project_id"],
        location=proj_cfg["location"],
        base_model=model_cfg["base_model"],
        tuned_model_display_name=model_cfg["tuned_display_name"],
        train_dataset_uri=data_cfg["train_uri"],
        validation_dataset_uri=data_cfg["validation_uri"],
        epochs=epochs,
        adapter_size=4,  # consistent with your current code
        learning_rate_multiplier=train_cfg.get("learning_rate", 1.0e-5),
    )

    print(f"✓ Tuning job launched: {job_name}")


def cmd_status(args):
    print("=== COMMAND: CHECK STATUS ===")
    status = check_status()
    print(f"✓ Current status: {status}")


def cmd_wait(args):
    print("=== COMMAND: WAIT FOR COMPLETION ===")
    result = wait_until_complete()
    print(f"✓ Job finished with status: {result}")


def cmd_get_model(args):
    print("=== COMMAND: GET TUNED MODEL ===")
    name = get_tuned_model_name()
    print(f"✓ Tuned model endpoint: {name}")


# -----------------------------
# CLI Entrypoint
# -----------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Gemini Fine-Tuning Task Runner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # tune
    p_tune = sub.add_parser("tune", help="Start a new tuning job")
    p_tune.add_argument("--epochs", type=int, help="Override number of epochs")
    p_tune.set_defaults(func=cmd_tune)

    # status
    p_status = sub.add_parser("status", help="Check tuning status")
    p_status.set_defaults(func=cmd_status)

    # wait
    p_wait = sub.add_parser("wait", help="Wait for job to finish")
    p_wait.set_defaults(func=cmd_wait)

    # get-model
    p_model = sub.add_parser("get-model", help="Get tuned model info")
    p_model.set_defaults(func=cmd_get_model)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
