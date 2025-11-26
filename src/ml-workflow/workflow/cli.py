import argparse

from model import run_collector, run_processor, run_trainer, run_all


# ============================================================
# CLI handlers
# ============================================================

def cmd_collector(args):
    run_collector()


def cmd_processor(args):
    run_processor()


def cmd_trainer(args):
    run_trainer(epochs=args.epochs)


def cmd_run_all(args):
    run_all(epochs=args.epochs)


# ============================================================
# Entrypoint
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="DnD Narrator MLOps Workflow CLI"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # collector
    p_collect = subparsers.add_parser("collector", help="Run data collector (CRD3 → raw GCS)")
    p_collect.set_defaults(func=cmd_collector)

    # processor
    p_proc = subparsers.add_parser("processor", help="Run data processor (raw → Gemini SFT JSONL)")
    p_proc.set_defaults(func=cmd_processor)

    # trainer
    p_train = subparsers.add_parser("trainer", help="Run model trainer (Gemini fine-tuning)")
    p_train.add_argument(
        "--epochs",
        type=int,
        default=1,
        help="Number of fine-tuning epochs (default: 1)",
    )
    p_train.set_defaults(func=cmd_trainer)

    # run-all
    p_all = subparsers.add_parser("run-all", help="Run full pipeline: collector → processor → trainer")
    p_all.add_argument(
        "--epochs",
        type=int,
        default=1,
        help="Number of fine-tuning epochs for trainer (default: 1)",
    )
    p_all.set_defaults(func=cmd_run_all)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
