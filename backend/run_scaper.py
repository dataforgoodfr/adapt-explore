import os
import sys
import subprocess
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
SRC_DIR = BACKEND_DIR / "src"

def run_scraper(spider_name: str) -> None:
    env = os.environ.copy()

    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        str(SRC_DIR)
        + (os.pathsep + existing_pythonpath if existing_pythonpath else "")
    )

    command = [sys.executable, "-m", "scrapy", "crawl", spider_name]

    subprocess.run(
        command,
        cwd=BACKEND_DIR,
        env=env,
        check=True,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("spider")
    args = parser.parse_args()

    run_scraper(args.spider)