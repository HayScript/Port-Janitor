#!/usr/bin/env python3
"""
Usage:
    python3 portkill.py 3000
    python3 portkill.py 8080 -f
"""

import argparse
import platform
import subprocess
import sys


def run(cmd):
  try:
    res = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True,
    )
    return res.stdout.strip()
  except:
    return ""


def find_pids(port):
  os_name = platform.system()
  pids = set()

  if os_name == "Windows":
    out = run(f"netstat -ano | findstr :{port}")
    for line in out.splitlines():
      parts = line.strip().split()
      if len(parts) >= 5 and parts[1].endswith(f":{port}"):
        pids.add(parts[-1])
  else:
    out = run(f"lsof -ti :{port}")
    if out:
      for line in out.splitlines():
        if line.strip().isdigit():
          pids.add(line.strip())

  return list(pids)


def kill_pid(pid):
  if platform.system() == "Windows":
    return run(f"taskkill /F /PID {pid}")
  else:
    return run(f"kill -9 {pid}")


def main():
  parser = argparse.ArgumentParser(
      description="Quickly kill whatever is squatting on your local port."
  )
  parser.add_argument("port", type=int, help="Port number (e.g. 3000, 8080)")
  parser.add_argument(
      "-f", "--force", action="store_true", help="Skip confirmation prompt"
  )
  args = parser.parse_args()

  pids = find_pids(args.port)

  if not pids:
    print(f"Port {args.port} is already free.")
    sys.exit(0)

  print(f"Found PID(s) on port {args.port}: {', '.join(pids)}")

  for pid in pids:
    if not args.force:
      ans = input(f"Kill PID {pid}? [y/N]: ").strip().lower()
      if ans != "y":
        continue

    res = kill_pid(pid)
    if res:
      print(f"Killed PID {pid}.")
    else:
      print(
          f"Failed to kill PID {pid}. Try running with sudo/admin privileges."
      )


if __name__ == "__main__":
  main()