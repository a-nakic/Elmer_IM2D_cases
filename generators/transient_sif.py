import re
import argparse
from pathlib import Path


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

DEFAULT_TEMPLATE = Path("templates/transient.sif")
DEFAULT_ENTITIES = Path("im/entities.sif")
DEFAULT_OUTPUT = Path("transient.sif")


# ---------------------------------------------------------
# Parse entities.sif
# ---------------------------------------------------------

def parse_entities(filename):
    """
    Parse Body and Boundary Condition IDs and names.

    Returns:
        bodies: dict[str, int]
        boundaries: dict[str, int]
    """

    text = Path(filename).read_text(encoding="utf-8")

    entities = {
        "bodies": {},
        "boundaries": {}
    }

    pattern = re.compile(
        r"^\s*(Body|Boundary Condition)\s+(\d+)\s*\n"
        r"(.*?)"
        r"^\s*End\s*$",
        re.MULTILINE | re.DOTALL
    )

    for match in pattern.finditer(text):
        entity_type = match.group(1)
        entity_id = int(match.group(2))
        content = match.group(3)

        name_match = re.search(
            r'^\s*Name\s*=\s*(.+?)\s*$',
            content,
            re.MULTILINE
        )

        if not name_match:
            raise ValueError(
                f"Missing Name for {entity_type} {entity_id}"
            )

        name = name_match.group(1).strip().strip('"')

        key = (
            "bodies"
            if entity_type == "Body"
            else "boundaries"
        )

        if name in entities[key]:
            raise ValueError(
                f"Duplicate {entity_type} name: {name}"
            )

        entities[key][name] = entity_id

    return entities


# ---------------------------------------------------------
# Validate entities
# ---------------------------------------------------------

def validate_entities(entities):

    required_bodies = [
        "U_plus",
        "W_minus",
        "V_plus",
        "U_minus",
        "W_plus",
        "V_minus",
        "StatorIron",
        "StatorWedges",
        "StatorAirgap",
        "RotorIron",
        "RotorAirgap",
    ]

    required_boundaries = [
        "OuterStator",
        "Sliding_Stator",
        "Sliding_Rotor",
        "InnerRotor",
    ]

    for name in required_bodies:
        if name not in entities["bodies"]:
            raise ValueError(
                f"Required body '{name}' not found in entities.sif"
            )

    for name in required_boundaries:
        if name not in entities["boundaries"]:
            raise ValueError(
                f"Required boundary '{name}' not found in entities.sif"
            )

    # Check that all rotor bars have sequential names.
    bars = {
        name: entity_id
        for name, entity_id in entities["bodies"].items()
        if re.fullmatch(r"Bar\d+", name)
    }

    if not bars:
        raise ValueError("No rotor bars found in entities.sif")

    return bars


# ---------------------------------------------------------
# Generate body definitions
# ---------------------------------------------------------

def generate_bodies(entities, bars):

    bodies = entities["bodies"]

    output = []

    # Rotor bars
    for name, body_id in sorted(
        bars.items(),
        key=lambda item: int(item[0][3:])
    ):
        output.append(f"""
Body {body_id}
  Name = "{name}"
  Equation = 1
  Material = 3
  Body Force = 7
  Torque Groups = Integer 1
End
""")

    # Stator windings
    winding_names = [
        "U_plus",
        "W_minus",
        "V_plus",
        "U_minus",
        "W_plus",
        "V_minus",
    ]

    for name in winding_names:
        body_id = bodies[name]

        output.append(f"""
Body {body_id}
  Name = {name}
  Equation = 1
  Material = 4
End
""")

    # Remaining bodies
    body_definitions = {
        "StatorIron": (2, False),
        "StatorWedges": (1, False),
        "StatorAirgap": (1, False),
        "RotorIron": (2, True),
        "RotorAirgap": (1, True),
    }

    for name, (material, rotating) in body_definitions.items():

        body_id = bodies[name]

        output.append(f"""
Body {body_id}
  Name = {name}
  Equation = 1
  Material = {material}""")

        if rotating:
            output.append("""
  Body Force = 7""")

        if name == "RotorIron":
            output.append("""
  Torque Groups = Integer 1""")

        if name == "RotorAirgap":
            output.append("""
  R Inner = Real 0.03525
  R Outer = Real 0.03541""")

        output.append("""
End
""")

    return "\n".join(output)


# ---------------------------------------------------------
# Generate components
# ---------------------------------------------------------

def generate_components(entities):

    bodies = entities["bodies"]

    components = [
        ("Uplus", "U_plus", 101),
        ("Vplus", "V_plus", 102),
        ("Wminus", "W_minus", 103),
        ("Uminus", "U_minus", 104),
        ("Vminus", "V_minus", 105),
        ("Wplus", "W_plus", 106),
    ]

    output = []

    for component_name, body_name, component_id in components:

        body_id = bodies[body_name]

        output.append(f"""
Component {component_id}
  Name = String {component_name}
  Body = Integer {body_id}
  Coil Type = String Stranded
  Number of Turns = Real $ Nph
  Resistance = Real $ Rs
End
""")

    return "\n".join(output)


# ---------------------------------------------------------
# Generate boundary conditions
# ---------------------------------------------------------

# def generate_boundaries(entities):

#     boundaries = entities["boundaries"]

#     definitions = {
#         "OuterStator": """
#   A = Real 0
# """,

#         "StatorRight": """
#   Mortar BC = Integer 3
#   Mortar BC Static = Logical True
#   Anti Radial Projector = Logical True
#   Galerkin Projector = Logical True
# """,

#         "StatorLeft": "",

#         "Sliding_Stator": """
#   Mortar BC = Integer 8
#   Anti Rotational Projector = Logical True
#   Galerkin Projector = Logical True
# """,

#         "InnerRotor": """
#   A = Real 0
# """,

#         "RotorRight": """
#   Mortar BC = Integer 7
#   Mortar BC Static = Logical True
#   Anti Radial Projector = Logical True
#   Galerkin Projector = Logical True
# """,

#         "RotorLeft": "",

#         "Sliding_Rotor": "",
#     }

#     # These boundary names must exist in entities.sif.
#     output = []

#     for name, properties in definitions.items():

#         if name not in boundaries:
#             continue

#         boundary_id = boundaries[name]

#         output.append(f"""
# Boundary Condition {boundary_id}
#   Name = {name}
# {properties}End
# """)

#     return "\n".join(output)



def generate_boundaries(entities):

    boundaries = entities["boundaries"]

    # Map each boundary to its mating boundary.
    mating_boundaries = {
        "StatorRight": "StatorLeft",
        "RotorRight": "RotorLeft",
        "Sliding_Stator": "Sliding_Rotor",
    }

    definitions = {
        "OuterStator": """
  A = Real 0
""",

        "StatorRight": """
  Mortar BC = Integer {mating_id}
  Mortar BC Static = Logical True
  Anti Radial Projector = Logical True
  Galerkin Projector = Logical True
""",

        "StatorLeft": "",

        "Sliding_Stator": """
  Mortar BC = Integer {mating_id}
  Anti Rotational Projector = Logical True
  Galerkin Projector = Logical True
""",

        "InnerRotor": """
  A = Real 0
""",

        "RotorRight": """
  Mortar BC = Integer {mating_id}
  Mortar BC Static = Logical True
  Anti Radial Projector = Logical True
  Galerkin Projector = Logical True
""",

        "RotorLeft": "",

        "Sliding_Rotor": "",
    }

    output = []

    for name, properties in definitions.items():

        if name not in boundaries:
            continue

        boundary_id = boundaries[name]

        # Replace mating boundary placeholder with its actual ID.
        if name in mating_boundaries:

            mating_name = mating_boundaries[name]

            if mating_name not in boundaries:
                raise ValueError(
                    f"Mating boundary '{mating_name}' "
                    f"for '{name}' not found in entities.sif"
                )

            mating_id = boundaries[mating_name]

            properties = properties.format(
                mating_id=mating_id
            )

        output.append(f"""
Boundary Condition {boundary_id}
  Name = {name}
{properties}End
""")

    return "\n".join(output)


# ---------------------------------------------------------
# Generate complete transient.sif
# ---------------------------------------------------------

def generate(template_file, entities_file, output_file):

    template = Path(template_file).read_text(
        encoding="utf-8"
    )

    entities = parse_entities(entities_file)

    bars = validate_entities(entities)

    # Generate dynamic sections.
    bodies = generate_bodies(entities, bars)
    components = generate_components(entities)
    boundaries = generate_boundaries(entities)

    # Replace body section.
    body_start = "!##################################### Bodies"
    component_start = "!##################################### Components"

    body_pattern = re.compile(
        re.escape(body_start) +
        r".*?" +
        re.escape(component_start),
        re.DOTALL
    )

    body_replacement = (
        "!##################################### Bodies "
        "#######################################\n"
        + bodies +
        "\n"
        + component_start
    )

    template, count = body_pattern.subn(
        lambda _: body_replacement,
        template,
        count=1
    )

    if count != 1:
        raise ValueError("Could not locate body section in template")

    # Replace component section.
    component_end = "!###############################################################################"

    component_pattern = re.compile(
        r'include "cage/cage\.definitions".*?'
        r'(?=' + re.escape(component_end) + r')',
        re.DOTALL
    )

    template, count = component_pattern.subn(
        lambda _: (
            'include "cage/cage.definitions"\n'
            + components
            + "\n"
        ),
        template,
        count=1
    )

    if count != 1:
        raise ValueError("Could not locate component section")

    # Replace boundary section.
    boundary_start = "!###############################################################################\n!#######################------ Boundary section"

    boundary_pattern = re.compile(
        re.escape(boundary_start) +
        r".*",
        re.DOTALL
    )

    boundary_replacement = (
        boundary_start + "\n"
        + boundaries
    )

    template, count = boundary_pattern.subn(
        lambda _: boundary_replacement,
        template,
        count=1
    )

    if count != 1:
        raise ValueError("Could not locate boundary section")

    # Check that no placeholders remain.
    unresolved = re.findall(r"<[^<>]+>", template)

    if unresolved:
        raise ValueError(
            "Unresolved template placeholders: "
            + ", ".join(unresolved)
        )

    # Write output.
    Path(output_file).write_text(
        template,
        encoding="utf-8"
    )

    print(f"Generated: {output_file}")
    print(f"Rotor bars: {len(bars)}")
    print(f"Bodies: {len(entities['bodies'])}")
    print(f"Boundaries: {len(entities['boundaries'])}")


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Generate transient.sif from entities.sif"
    )

    parser.add_argument(
        "--template",
        default=DEFAULT_TEMPLATE
    )

    parser.add_argument(
        "--entities",
        default=DEFAULT_ENTITIES
    )

    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT
    )

    args = parser.parse_args()

    generate(
        args.template,
        args.entities,
        args.output
    )
