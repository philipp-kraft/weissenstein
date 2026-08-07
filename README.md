# weissenstein

Automation for running CoreMark on a Xilinx Genesys2 FPGA and sweeping CVA6 microarchitectural parameters to explore their effect. Named after `weissenstein`, the remote host that owns the FPGA boards (booked via its `fpga` CLI).

## Layout

- [fpga.py](fpga.py): books an FPGA board on `weissenstein`, optionally
  synthesizes/programs/flashes it, loads a ELF and watches the UART log for a match string.
- [sweep.py](sweep.py): drives `fpga.py` across a table of microarchitectural parameter
  overrides (`SWEEPS`), patching `hw/cheshire_pkg.sv` synthesizing a bitstream per point and recording the result.
- [dashboard.py](dashboard.py): Dash web app that plots the sweep results from `results/`.
- `bitstreams/`: one saved `.bit` per sweep point, so a point
  can be re-run without re-synthesizing.
- `results/`: sweep output CSVs: `name, score, score_mhz, log_dir, error, timestamp, params`.
- `logs/`: per-run directories, timestamped `YYYYMMDD_HHMMSS/`, each with `fpga.log`, `uart.log`, `openocd.log`, `gdb.log`.

## Requirements

- `pip install -r requirements.txt`.
- SSH access to `weissenstein` (passwordless), with the `fpga` CLI.
- `riscv64-unknown-elf-gdb` on `PATH` locally.
- Run from a full Cheshire checkout.

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

Each `fpga.py` invocation books the board with a 1h lease and releases it automatically, even on failure.

Run the full parameter sweep (skips points already scored in the results
CSV, reusing a saved bitstream when present instead of re-synthesizing):

```
./sweep.py
```

View the results:

```
./dashboard.py
```

Serves at `http://127.0.0.1:8050`, reading whatever CSVs are in `results/`.
