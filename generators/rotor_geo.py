
#!/usr/bin/env python3
"""Generate im_rotor.geo and model.sif for an Elmer/Gmsh motor model."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.request import urlopen


GEO_URL = (
    "https://raw.githubusercontent.com/pavelponomarev/"
    "Elmer_IM2D_cases/master/IM_one_pole/gmsh/im_rotor.geo"
)

SIF_URL = (
    "https://raw.githubusercontent.com/pavelponomarev/"
    "Elmer_IM2D_cases/master/IM_one_pole/model.sif"
)


def download_template(url: str) -> str:
    """Download an original template from the GitHub repository."""
    with urlopen(url, timeout=30) as response:
        return response.read().decode("utf-8")


def replace_parameter(text: str, name: str, value: int | float) -> str:
    """Replace a top-level Gmsh parameter assignment."""
    pattern = rf"(?m)^(\s*{re.escape(name)}\s*=\s*)[^;]+(;)"
    updated, count = re.subn(
        pattern,
        lambda m: f"{m.group(1)}{value};",
        text,
        count=1,
    )
    if count != 1:
        raise ValueError(f"Could not find parameter {name!r} in geometry.")
    return updated


def generate_rotor_geo(
    *,
    Qr: int = 40,
    N_rs: int = 10,
    R_rin: float = 27,
    R_rout: float = 62,
    R_g: float = 62.25,
    b_1: float = 1,
    h_1: float = 0.4,
    b_4: float = 4.4,
    b_5: float = 2,
    h_5: float = 12,
    template: str | None = None,
) -> str:
    """Generate Gmsh geometry with the requested number of rotor bars."""

    validate_parameters(Qr, N_rs, R_rin, R_rout, R_g,
                        b_1, h_1, b_4, b_5, h_5)

    if template is not None:
        text = Path(template).read_text(encoding="utf-8")
    else:
        text = download_template(GEO_URL)

    parameters = {
        "Qr": Qr,
        "N_rs": N_rs,
        "R_rin": R_rin,
        "R_rout": R_rout,
        "R_g": R_g,
        "b_1": b_1,
        "h_1": h_1,
        "b_4": b_4,
        "b_5": b_5,
        "h_5": h_5,
    }

    for name, value in parameters.items():
        text = replace_parameter(text, name, value)

    # Each slot consists of two half-surfaces in RotorConductor_[].
    # Group each pair into one named physical bar.
    bar_groups = []
    for i in range(N_rs):
        first_surface = 2 * i
        second_surface = first_surface + 1
        bar_number = i + 1
        bar_groups.append(
            f'Physical Surface("Bar{bar_number}") = '
            f'{{RotorConductor_[{{{first_surface},{second_surface}}}]}};'
        )

    bar_block = "\n".join(bar_groups) + "\n\n"

    # Replace only the existing bar declarations; keep the other
    # physical surfaces and all boundary definitions intact.
    pattern = (
        r'(?m)^Physical Surface\("Bar1"\).*?'
        r'(?=^Physical Surface\("RotorIron"\))'
    )
    text, count = re.subn(
        pattern,
        lambda _: bar_block,
        text,
        count=1,
        flags=re.DOTALL | re.MULTILINE,
    )
    if count != 1:
        raise ValueError("Could not locate the physical bar declarations.")

    return text


def validate_parameters(
    Qr: int,
    N_rs: int,
    R_rin: float,
    R_rout: float,
    R_g: float,
    b_1: float,
    h_1: float,
    b_4: float,
    b_5: float,
    h_5: float,
) -> None:
    """Basic checks for valid rotor geometry inputs."""

    if not isinstance(Qr, int) or isinstance(Qr, bool) or Qr < 1:
        raise ValueError("Qr must be a positive integer.")

    if (
        not isinstance(N_rs, int)
        or isinstance(N_rs, bool)
        or not 1 <= N_rs <= Qr
    ):
        raise ValueError("N_rs must be an integer between 1 and Qr.")

    if not (0 < R_rin < R_rout < R_g):
        raise ValueError("Require 0 < R_rin < R_rout < R_g.")

    if min(b_1, h_1, b_4, b_5, h_5) <= 0:
        raise ValueError("All slot dimensions must be positive.")

    if b_1 >= 2 * R_rout or b_1 >= b_4:
        raise ValueError("Slot opening width b_1 is too large.")

    if b_1 >= b_4:
        raise ValueError("Require b_1 < b_4.")


def generate_files(
    output_dir: str | Path = ".",
    *,
    template: str | Path | None = None,
    Qr: int = 40,
    N_rs: int = 10,
    R_rin: float = 27,
    R_rout: float = 62,
    R_g: float = 62.25,
    b_1: float = 1,
    h_1: float = 0.4,
    b_4: float = 4.4,
    b_5: float = 2,
    h_5: float = 12,
) -> None:
    """Generate rotor geometry using a local or remote template."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    geo = generate_rotor_geo(
        template=template,
        Qr=Qr,
        N_rs=N_rs,
        R_rin=R_rin,
        R_rout=R_rout,
        R_g=R_g,
        b_1=b_1,
        h_1=h_1,
        b_4=b_4,
        b_5=b_5,
        h_5=h_5,
    )

    output_path = output_dir / "im_rotor.geo"
    output_path.write_text(geo, encoding="utf-8")

    print(f"Generated: {output_path}")
    print(f"Rotor slots/bars: {N_rs}")
    print(f"Rotor teeth parameter Qr: {Qr}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate the Gmsh rotor geometry and Elmer model."
    )
    parser.add_argument("--output-dir", default=".")
    parser.add_argument("--Qr", type=int, default=40)
    parser.add_argument("--N_rs", type=int, default=10)
    parser.add_argument("--R_rin", type=float, default=27)
    parser.add_argument("--R_rout", type=float, default=62)
    parser.add_argument("--R_g", type=float, default=62.25)
    parser.add_argument("--b_1", type=float, default=1)
    parser.add_argument("--h_1", type=float, default=0.4)
    parser.add_argument("--b_4", type=float, default=4.4)
    parser.add_argument("--b_5", type=float, default=2)
    parser.add_argument("--h_5", type=float, default=12)
    parser.add_argument(
        "--template",
        type=Path,
        default=None,
        help="Path to a local im_rotor.geo template (defaults to GitHub).",
    )

    args = parser.parse_args()
    options = vars(args)
    output_dir = options.pop("output_dir")
    generate_files(output_dir, **options)


if __name__ == "__main__":
    main()
