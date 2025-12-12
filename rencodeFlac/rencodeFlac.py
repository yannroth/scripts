import argparse
import os
import subprocess
import tempfile
from pathlib import Path


def run_allow_errors(cmd):
    """
    Run a command, but DO NOT stop on non-zero return codes.
    Returns (returncode, stdout, stderr).
    """
    print("Running:", " ".join(cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def reencode_flac(input_path: Path, output_dir: Path, flac_bin: str = "flac", flac_decoder: str = "flac"):
    """
    Decode a FLAC file to a temporary WAV (ignoring decode errors),
    then re-encode it.
    """
    output_path = output_dir / input_path.name
    output_path = output_path.with_suffix(".flac")

    with tempfile.TemporaryDirectory() as tmpdir:
        wav_path = Path(tmpdir) / "decoded.wav"

        # --- Step 1: decode with error tolerance ---
        decode_cmd = [
            flac_decoder,
            "-d",
            "-F",          # <-- prevents abort on errors
            str(input_path),
            "-o", str(wav_path)
        ]
        rc, out, err = run_allow_errors(decode_cmd)

        if rc != 0:
            print(f"⚠ Decode reported errors for {input_path.name}:")
            print(err)

        if not wav_path.exists():
            print(f"❌ No WAV produced for {input_path.name}, skipping.")
            return

        # --- Step 2: re-encode ---
        encode_cmd = [
            flac_bin,
            str(wav_path),
            "-o", str(output_path)
        ]
        rc, out, err = run_allow_errors(encode_cmd)

        if rc != 0:
            print(f"⚠ Encode reported errors for {input_path.name}:")
            print(err)
        else:
            print(f"✔ Re-encoded: {input_path.name} → {output_path}")


def main():
    examples = """Usage examples:
    To decode using the flac v.1.2.1 binary:
        python rencodeFlac.py -i flac_folder --decoder-bin ../flac121/bin/flac
            
    To simply decode and re-encode flac in current folder:
        python rencodeFlac.py"""
    parser = argparse.ArgumentParser(
        description="Batch decode+re-encode FLACs, continuing past corruption.",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-i", "--input",
        default=".",
        help="Input directory containing FLAC files (default: current directory)"
    )
    parser.add_argument(
        "-o", "--output",
        default="re-encode",
        help="Output directory for re-encoded FLAC files (default: re-encode)"
    )
    parser.add_argument(
        "--flac-bin",
        default="flac",
        help="Path to flac binary (default: system 'flac')"
    )
    parser.add_argument(
        "--decoder-bin",
        default="flac",
        help="FLAC binary used for decoding (default: system 'flac')"
    )

    args = parser.parse_args()

    in_dir = Path(args.input).resolve()
    out_dir = Path(args.output).resolve()

    if not in_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {in_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)

    flac_files = sorted(in_dir.glob("*.flac"))

    if not flac_files:
        print("No FLAC files found in:", in_dir)
        return

    print(f"Found {len(flac_files)} FLAC files.")
    print(f"Output directory: {out_dir}")

    for f in flac_files:
        reencode_flac(f, out_dir, args.flac_bin, args.decoder_bin)

    print("\nDone.")


if __name__ == "__main__":
    main()
