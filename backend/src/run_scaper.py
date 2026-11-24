
import subprocess
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent

data_dir = backend_dir / "data"
data_dir.mkdir(parents=True, exist_ok=True)

subprocess.run(
    [
        sys.executable,
        "-m",
        "scrapy",
        "crawl",
        "adaptaville"
    ],
    cwd=backend_dir,
    check=True
)
