#!/usr/bin/env  python3

import ollama
from size import Size

import time


def main(interval: int) -> None:
    template = (
        "{name:<20} {size_human}/{vram_used} ({gpu_percent}%/{cpu_percent}% GPU/CPU)"
    )
    while True:
        try:
            models = ollama.ps()["models"]
            for model in models:
                size, vram = model["size"], model["size_vram"]
                model["size_human"] = str(Size(size)).strip(" GB")
                model["vram_used"] = str(Size(vram))
                model["gpu_percent"] = f"{(vram / size) * 100:.0f}"
                model["cpu_percent"] = f"{100 - float(model['gpu_percent']):.0f}"
                print(template.format(**model))
            time.sleep(interval)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(interval)


if __name__ == "__main__":
    import sys

    interval = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    main(int(interval))
