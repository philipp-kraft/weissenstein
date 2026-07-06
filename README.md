# weissenstein

Automation for running CoreMark on a Xilinx Genesys2 FPGA and sweeping CVA6 microarchitectural parameters to explore their effect. Named after `weissenstein`, the remote host that owns the FPGA boards (booked via its `fpga` CLI).

## Layout

- [fpga.py](fpga.py) — books an FPGA board on `weissenstein`, optionally
  synthesizes/programs/flashes it, loads a baremetal ELF via GDB+OpenOCD over
  JTAG, and watches the UART log for a match string.
- [sweep.py](sweep.py) — drives `fpga.py` across a table of CVA6 parameter
  overrides (`SWEEPS`), patching `hw/cheshire_pkg.sv`'s `DefaultCfg`,
  synthesizing a bitstream per point, and recording the benchmark result to CSV.
- `bitstreams/` — one saved `.bit` per sweep point, so a point
  can be re-run (e.g. re-flashed, or re-run after a UART timeout) without
  re-synthesizing.
- `results/` — sweep output CSVs: `name, score, score_mhz,
  log_dir, error, timestamp, params`.
- `logs/` — per-run directories, timestamped `YYYYMMDD_HHMMSS/`, each with
  `fpga.log`, `uart.log`, `openocd.log`, `gdb.log`.

## Requirements

- SSH access to `weissenstein` (passwordless), with the `fpga`.
- `riscv64-unknown-elf-gdb` on `PATH` locally.
- Run from a full Cheshire checkout, both scripts locate the repo root as
  the parent of this directory and shell out to `make chs-xilinx-*` targets
  there for synthesis, programming, and flashing.

## Usage

Single run, loading the default CoreMark ELF via GDB against whatever
bitstream is already on the board:

```
./fpga.py
```

Synthesize, program, and flash before running:

```
./fpga.py --synth --program --flash
```

Load a different ELF, or wait for a different UART match string:

```
./fpga.py --binary path/to/test.elf --match "PASS"
```

Run the full parameter sweep (skips points already scored in the results
CSV, reusing a saved bitstream when present instead of re-synthesizing):

```
./sweep.py
```

Each `fpga.py` invocation books the board with a 1h lease and releases it automatically, even on failure.
