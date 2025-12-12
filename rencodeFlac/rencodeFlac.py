import argparse
from pathlib import Path
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

def run_allow_errors(cmd):
    """Run a command and capture output. Returns returncode, stdout, stderr."""
    print("Running:", " ".join(cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr

def reencode_flac(input_path: Path, output_dir: Path, decoder_bin: str, encoder_bin: str):
    """Decode a FLAC file to WAV, then re-encode it, ignoring decode errors."""
    output_path = output_dir / input_path.name
    output_path = output_path.with_suffix(".flac")

    with tempfile.TemporaryDirectory() as tmpdir:
        wav_path = Path(tmpdir) / "decoded.wav"

        # Step 1: decode
        decode_cmd = [decoder_bin, "-d", "-F", str(input_path), "-o", str(wav_path)]
        rc, _, err = run_allow_errors(decode_cmd)
        if rc != 0:
            print(f"⚠ Decode reported errors for {input_path.name}: {err}")
        if not wav_path.exists():
            print(f"❌ No WAV produced for {input_path.name}, skipping.")
            return

        # Step 2: encode
        encode_cmd = [encoder_bin, str(wav_path), "-o", str(output_path)]
        rc, _, err = run_allow_errors(encode_cmd)
        if rc != 0:
            print(f"⚠ Encode reported errors for {input_path.name}: {err}")
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
    parser = argparse.ArgumentParser(description="Batch decode+re-encode FLACs with parallel threads.")
    parser.add_argument("-i", "--input", default=".", help="Input directory containing FLAC files")
    parser.add_argument("-o", "--output", default="re-encode", help="Output directory for re-encoded FLAC files")
    parser.add_argument("--decoder-bin", default="flac", help="FLAC binary used for decoding")
    parser.add_argument("--encoder-bin", default="flac", help="FLAC binary used for encoding")
    parser.add_argument("-j", "--jobs", type=int, default=os.cpu_count(), help="Number of parallel threads")
    args = parser.parse_args()

    in_dir = Path(args.input).resolve()
    out_dir = Path(args.output).resolve()
    decoder_bin = args.decoder_bin
    encoder_bin = args.encoder_bin
    threads = args.jobs

    if not in_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {in_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)

    flac_files = sorted(in_dir.glob("*.flac"))
    if not flac_files:
        print("No FLAC files found in:", in_dir)
        return

    print(f"Found {len(flac_files)} FLAC files.")
    print(f"Using {threads} threads.")
    print(f"Output directory: {out_dir}")

    # --- parallel processing ---
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(reencode_flac, f, out_dir, decoder_bin, encoder_bin): f
            for f in flac_files
        }
        for future in as_completed(futures):
            file = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"❌ Error processing {file.name}: {e}")

    print("\nDone.")

if __name__ == "__main__":
    main()
