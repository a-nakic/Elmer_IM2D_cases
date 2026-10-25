#!/usr/bin/env python3
"""Generate a full-machine Elmer case from total tooth counts.

This entry point uses separate modules for each generation task:
- stator geometry
- rotor geometry
- steady-state model .sif
- transient .sif
- harmonic .sif
"""

from __future__ import annotations

import argparse
from pathlib import Path

from generators.harmonic_sif import generate_harmonic_sif
from generators.model_sif import generate_model_sif
from generators.rotor_geo import generate_rotor_geo
from generators.stator_geo import generate_stator_geo
from generators.transient_sif import generate_transient_sif


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a full-machine Elmer IM case.")
    parser.add_argument("--qs", type=int, default=48, help="Total stator teeth")
    parser.add_argument("--qr", type=int, default=40, help="Total rotor teeth")
    parser.add_argument("--ns", type=int, default=48, help="Stator sector count to generate")
    parser.add_argument("--nr", type=int, default=40, help="Rotor sector count to generate")
    parser.add_argument("--out-dir", type=Path, default=Path("IM_full_machine"), help="Output directory")
    args = parser.parse_args()

    out_dir = args.out_dir
    (out_dir / "gmsh").mkdir(parents=True, exist_ok=True)

    generate_stator_geo(out_dir / "gmsh" / "im_stator.geo", qs=args.qs, ns=args.ns)
    generate_rotor_geo(out_dir / "gmsh" / "im_rotor.geo", qr=args.qr, nr=args.nr)
    generate_model_sif(out_dir / "model.sif", rotor_bars=args.nr)
    generate_transient_sif(out_dir / "transient.sif", rotor_bars=args.nr)
    generate_harmonic_sif(out_dir / "harmonic.sif", rotor_bars=args.nr)

    print(f"Generated full-machine case in {out_dir}")


if __name__ == "__main__":
    main()
