import re
from pathlib import Path
from urllib.request import urlopen

SIF_URL = (
    "https://raw.githubusercontent.com/pavelponomarev/"
    "Elmer_IM2D_cases/master/IM_one_pole/model.sif"
)

# Stator winding phase -> Body Force ID
WINDING_FORCES = {
    "U_plus": 2,
    "V_plus": 3,
    "W_minus": 4,
    "U_minus": 5,
    "V_minus": 6,
    "W_plus": 7,
}


def parse_entity_bodies(entities_path):
    """Read body names and IDs from entities.sif."""
    text = Path(entities_path).read_text(encoding="utf-8")

    pattern = re.compile(
        r"(?ms)^[ \t]*Body[ \t]+(\d+)[ \t]*\r?\n"
        r"(.*?)^[ \t]*End[ \t]*$"
    )

    bodies = {}

    for match in pattern.finditer(text):
        body_id = int(match.group(1))
        name_match = re.search(
            r'(?m)^[ \t]*Name[ \t]*=[ \t]*"?([^"\r\n]+?)"?[ \t]*$',
            match.group(2),
        )

        if not name_match:
            continue

        name = name_match.group(1).strip()

        if name in bodies:
            raise ValueError(f"Duplicate body name: {name}")

        if body_id in bodies.values():
            raise ValueError(f"Duplicate body ID: {body_id}")

        bodies[name] = body_id

    if not bodies:
        raise ValueError(f"No body definitions found in {entities_path}")

    return bodies


def make_body_block(name, body_id):
    """Build a complete Elmer body definition from its physical role."""

    lines = [
        f"Body {body_id}",
        f"  Name = {name}",
        "  Equation = 1",
    ]

    # Stator winding regions.
    if name in WINDING_FORCES:
        lines.extend([
            "  Material = 1",
            f"  Body Force = {WINDING_FORCES[name]}",
        ])

    # Rotor conductor bars: rotating air/conductor material.
    elif re.fullmatch(r"Bar\d+", name):
        lines.extend([
            "  Material = 1",
            "  Body Force = 1",
        ])

    # Iron regions.
    elif name in ("StatorIron", "RotorIron"):
        lines.append("  Material = 2")

        if name == "RotorIron":
            lines.append("  Body Force = 1")

    # Nonconducting air and wedge regions.
    elif name in ("StatorWedges", "StatorAirgap"):
        lines.append("  Material = 1")

    elif name == "RotorAirgap":
        lines.extend([
            "  Material = 1",
            "  Body Force = 1",
        ])

    else:
        raise ValueError(
            f"Unknown body name {name!r} (ID {body_id}). "
            "Add its material/force rule to make_body_block()."
        )

    lines.append("End")
    return "\n".join(lines)


def generate_model_sif(
    entities_path="entities.sif",
    template_path=None,
    output_path="model.sif",
):
    """
    Generate model.sif using IDs from entities.sif.

    The template supplies all non-body configuration, including
    materials, Body Force definitions, solvers and boundary conditions.
    """

    entities = parse_entity_bodies(entities_path)

    if template_path:
        template = Path(template_path).read_text(encoding="utf-8")
    else:
        with urlopen(SIF_URL, timeout=30) as response:
            template = response.read().decode("utf-8")

    # Generate every body using the actual ID from entities.sif.
    ordered_bodies = sorted(
        entities.items(),
        key=lambda item: item[1],
    )

    body_blocks = [
        make_body_block(name, body_id)
        for name, body_id in ordered_bodies
    ]

    new_body_section = (
        "!------ Skeleton for body section -----\n\n"
        + "\n\n".join(body_blocks)
        + "\n\n"
    )

    # Replace the entire body section, not just the bodies already
    # present in the template. Leave solvers and BCs unchanged.
    start_marker = "!------ Skeleton for body section -----"
    solver_marker = "!#######################------ Solver section"

    start = template.find(start_marker)
    if start == -1:
        raise ValueError(
            "Could not find the body-section marker in model.sif template."
        )

    end = template.find(solver_marker, start)
    if end == -1:
        raise ValueError(
            "Could not find the solver-section marker after the body section."
        )

    updated = (
        template[:start]
        + new_body_section
        + template[end:]
    )

    Path(output_path).write_text(updated, encoding="utf-8")

    bar_names = [
        name for name in entities
        if re.fullmatch(r"Bar\d+", name)
    ]

    print(f"Generated: {output_path}")
    print(f"Total bodies: {len(entities)}")
    print(f"Rotor bars: {len(bar_names)}")
    print("Winding body forces:")
    for name, force_id in WINDING_FORCES.items():
        if name in entities:
            print(f"  {name}: Body Force = {force_id}")
    print("Rotor rotation force: Body Force = 1")


if __name__ == "__main__":
    generate_model_sif(
        entities_path="im/entities.sif",
        template_path="templates/model.sif",
        output_path="model.sif",
    )
