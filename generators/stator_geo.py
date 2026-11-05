
#!/usr/bin/env python3
"""Generate parameterized Gmsh stator geometry."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.request import urlopen


TEMPLATE_URL = (
    "https://raw.githubusercontent.com/pavelponomarev/"
    "Elmer_IM2D_cases/master/IM_one_pole/gmsh/im_stator.geo"
)


DEFAULTS = {
    "Qs": 48,
    "N_ss": 12,
    "R_sin": 62.5,
    "R_sout": 110,
    "R_g": 62.25,
    "b_5": 6.8,
    "b_1": 2.8,
    "h_1": 0.7,
    "h_2": 0.2,
    "b_4": 4.0,
    "h_5": 24.0,
    "m_coarse": 20,
    "m_normal": 12,
    "m_gap": 0.55,
    "m_sl_top": 7.0,
    "m_sl_bot": 2.0,
    "m_s_out": 12.0,
    "qq": 2,
    "y_p": 5,
    "h_w0": 0.5,
}


def validate_parameters(p: dict) -> None:
    """Validate the stator parameters before generating the geometry."""

    Qs = p["Qs"]
    N_ss = p["N_ss"]

    if not isinstance(Qs, int) or isinstance(Qs, bool) or Qs < 1:
        raise ValueError("Qs must be a positive integer.")

    if (
        not isinstance(N_ss, int)
        or isinstance(N_ss, bool)
        or not 1 <= N_ss <= Qs
    ):
        raise ValueError("N_ss must be an integer between 1 and Qs.")

    # The original template uses four slots per phase belt.
    if N_ss % 4 != 0:
        raise ValueError(
            "N_ss must be divisible by 4 for the original phase assignment."
        )

    if not (0 < p["R_g"] < p["R_sin"] < p["R_sout"]):
        raise ValueError(
            "Require 0 < R_g < R_sin < R_sout."
        )

    for name in ("b_1", "h_1", "h_2", "b_4", "b_5", "h_5"):
        if p[name] <= 0:
            raise ValueError(f"{name} must be positive.")

    if p["b_1"] >= p["b_4"]:
        raise ValueError("Require b_1 < b_4.")

    for name in (
        "m_coarse",
        "m_normal",
        "m_gap",
        "m_sl_top",
        "m_sl_bot",
        "m_s_out",
    ):
        if p[name] <= 0:
            raise ValueError(f"{name} must be positive.")


def load_template(template_path: str | Path | None = None) -> str:
    """Load the original geometry from a local file or GitHub."""

    if template_path is not None:
        return Path(template_path).read_text(encoding="utf-8")

    with urlopen(TEMPLATE_URL, timeout=30) as response:
        return response.read().decode("utf-8")



def replace_gmsh_parameter(
    text: str,
    name: str,
    value: int | float,
) -> str:
    """Replace a Gmsh parameter value without changing its comment."""

    pattern = re.compile(
        rf"(?m)^([ \t]*{re.escape(name)}[ \t]*=[ \t]*)"
        rf"[^;\r\n]*(?=;)"
    )

    updated, count = pattern.subn(
        lambda match: f"{match.group(1)}{value}",
        text,
        count=1,
    )

    if count != 1:
        raise ValueError(
            f"Could not find assignment for {name!r}. "
            "Check the template path and parameter spelling."
        )

    return updated



def generate_stator_geo(
    *,
    template_path: str | Path | None = None,
    **overrides,
) -> str:
    """
    Generate im_stator.geo.

    Supported arguments:
        Qs, N_ss, R_sin, R_sout, R_g,
        b_5, b_1, h_1, h_2, b_4, h_5,
        m_coarse, m_normal, m_gap,
        m_sl_top, m_sl_bot, m_s_out.
    """

    unknown = set(overrides) - set(DEFAULTS)
    if unknown:
        raise TypeError(
            f"Unknown parameter(s): {', '.join(sorted(unknown))}"
        )

    parameters = {**DEFAULTS, **overrides}
    validate_parameters(parameters)

    text = load_template(template_path)

    for name, value in parameters.items():
        text = replace_gmsh_parameter(text, name, value)

    return text


def generate_file(
    output_path: str | Path = "im_stator.geo",
    *,
    template_path: str | Path | None = None,
    **parameters,
) -> Path:
    """Generate and save the Gmsh stator geometry."""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    geometry = generate_stator_geo(
        template_path=template_path,
        **parameters,
    )

    output_path.write_text(geometry, encoding="utf-8")

    print(f"Generated: {output_path}")
    print(f"Stator teeth Qs: {parameters.get('Qs', DEFAULTS['Qs'])}")
    print(f"Modeled slots N_ss: {parameters.get('N_ss', DEFAULTS['N_ss'])}")

    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate parameterized Gmsh stator geometry."
    )

    parser.add_argument("--output", default="im_stator.geo")
    parser.add_argument("--template", default=None)

    for name, default in DEFAULTS.items():
        parser.add_argument(
            f"--{name}",
            type=int if isinstance(default, int) else float,
            default=default,
        )

    args = vars(parser.parse_args())
    output = args.pop("output")
    template = args.pop("template")

    generate_file(
        output,
        template_path=template,
        **args,
    )


if __name__ == "__main__":
    main()
