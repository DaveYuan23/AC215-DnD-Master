import argparse
import os
import sys

# ------------------------------------------------------------
# Ensure workflow/ root is added to PYTHONPATH
# ------------------------------------------------------------
# This setup allows the script to correctly import 'model'
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 假设 model.py 和 cli.py 都在 workflow 目录下
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR)) 
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# 确保能导入 workflow/model.py 里的函数
# 如果 model.py 在上层目录，则需要调整 ROOT_DIR
try:
    from model import run_collector, run_processor, run_trainer, run_all
except ImportError:
    # 如果 model.py 在 workflow 的父目录，尝试父目录导入
    sys.path.insert(0, os.path.abspath(os.path.join(CURRENT_DIR, "..")))
    from model import run_collector, run_processor, run_trainer, run_all


# ============================================================
# CLI handlers
# ============================================================

def cmd_collector(args):
    print("=== Running Data Collector ===")
    run_collector()


def cmd_processor(args):
    print("=== Running Data Processor ===")
    run_processor()


def cmd_trainer(args):
    print(f"=== Running Trainer (epochs={args.epochs}) ===")
    run_trainer(epochs=args.epochs)


def cmd_run_all(args):
    print(f"=== Running Full MLOps Pipeline (epochs={args.epochs}) ===")
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
    p_collect = subparsers.add_parser(
        "collector",
        help="Run data collector (CRD3 → raw GCS)"
    )
    p_collect.set_defaults(func=cmd_collector)

    # processor
    p_proc = subparsers.add_parser(
        "processor",
        help="Run data processor (raw → Gemini SFT JSONL)"
    )
    p_proc.set_defaults(func=cmd_processor)

    # trainer
    p_train = subparsers.add_parser(
        "trainer",
        help="Run model trainer (Gemini fine-tuning)"
    )
    p_train.add_argument(
        "--epochs",
        type=int,
        default=1,
        help="Number of fine-tuning epochs (default: 1)"
    )
    p_train.set_defaults(func=cmd_trainer)

    # pipeline
    p_all = subparsers.add_parser(
        "run-all",
        help="Run full pipeline: collector → processor → trainer"
    )
    p_all.add_argument(
        "--epochs",
        type=int,
        default=1,
        help="Number of fine-tuning epochs for trainer (default: 1)"
    )
    p_all.set_defaults(func=cmd_run_all)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()