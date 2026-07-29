#!/usr/bin/env python3
"""Audacity control bridge via mod-script-pipe (named pipes).

Audacity exposes a scripting pipe when the mod-script-pipe module is enabled:
  /tmp/audacity_script_pipe.to.<uid>    (we write commands here)
  /tmp/audacity_script_pipe.from.<uid>  (we read responses here)

Each command is 'CommandName: Param=Value ...\\n'; the response ends with
'BatchCommand finished: OK'. This gives full control: generators (Tone/Chirp/
Noise), effects (Reverb/Echo/LowPass/...), selection, and Export2 to .ogg/.wav.

Usage:
    python aud.py do 'Tone: Frequency=440 Amplitude=0.5 Waveform=Sine'
    python aud.py version
"""
import fcntl
import os
import select
import sys
import time

UID = os.getuid()
TO = f"/tmp/audacity_script_pipe.to.{UID}"
FROM = f"/tmp/audacity_script_pipe.from.{UID}"


class Audacity:
    def __init__(self):
        if not (os.path.exists(TO) and os.path.exists(FROM)):
            raise RuntimeError("Audacity scripting pipes not found — is Audacity running "
                               "with mod-script-pipe enabled?")
        self._to = open(TO, "w")
        # Raw non-blocking fd so select() is authoritative (no stdio buffering surprises).
        self._fd = os.open(FROM, os.O_RDONLY | os.O_NONBLOCK)
        self._drain()

    def _drain(self):
        while select.select([self._fd], [], [], 0.05)[0]:
            if not os.read(self._fd, 65536):
                break

    def do(self, command, timeout=20.0):
        self._to.write(command + "\n")
        self._to.flush()
        return self._read(timeout)

    def _read(self, timeout):
        data = b""
        deadline = time.time() + timeout
        while True:
            # Audacity terminates each response with a blank line -> "...OK\n\n".
            if data.endswith(b"\n\n") and len(data) > 1:
                break
            rem = deadline - time.time()
            if rem <= 0:
                raise TimeoutError(f"no complete response within {timeout}s (got: {data[:160]!r})")
            if select.select([self._fd], [], [], rem)[0]:
                chunk = os.read(self._fd, 65536)
                if chunk:
                    data += chunk
                else:
                    time.sleep(0.01)
        return data.decode("utf-8", "replace")

    def ok(self, command):
        r = self.do(command)
        if "BatchCommand finished: OK" not in r and "finished: OK" not in r:
            raise RuntimeError(f"Audacity command failed:\n  cmd: {command}\n  resp: {r.strip()}")
        return r

    def close(self):
        try:
            self._to.close()
            self._from.close()
        except Exception:
            pass


def main():
    a = Audacity()
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    if cmd == "version":
        print(a.do("GetInfo: Type=Version").strip())
    elif cmd == "do":
        print(a.do(sys.argv[2]).strip())
    else:
        print(a.do(" ".join(sys.argv[1:])).strip())


if __name__ == "__main__":
    main()
