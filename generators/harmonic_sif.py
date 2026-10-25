from __future__ import annotations

from pathlib import Path


def generate_harmonic_sif(path: str | Path, rotor_bars: int = 40) -> None:
    rotor_bodies = "\n".join(
        f'''Body {i}
  Name = Bar{i}
  Equation = 1
  Material = 3
  Body Force = 2
  Torque Groups = Integer 1
End
''' for i in range(1, rotor_bars + 1)
    )

    content = f'''include harmonic_params.dat

Header
  Mesh DB "im"
  Results Directory "results"
  Include Path "materials"
End

Simulation
  Max Output Level = 3
  Coordinate System = Cartesian 2D
  Coordinate Scaling = 0.001
  Simulation Type = Steady
  Steady State Max Iterations = 2
  Circuit Model Depth = Real $ l
  Angular Frequency = Real $ 2*pi*f
  Mesh Levels = 2
  Mesh Keep = 1
  Use Mesh Names = Logical True
End

Material 1
  Relative Permeability = 1
  Electric Conductivity = 0
End

Material 2
  Name = "Iron"
  Relative Permeability = 300
  Electric Conductivity = 0
End

Material 3
  Relative Permeability = 1
  Electric Conductivity = Real $ 24000000*slip
End

Material 4
  Relative Permeability = 1
  Electric Conductivity = 48e6
End

Body Force 1
  Name = "Circuit"
  U_u Re = Real $ sqrt(2)/sqrt(3)*400*cos(0)
  U_u Im = Real $ sqrt(2)/sqrt(3)*400*sin(0)
  U_v Re = Real $ sqrt(2)/sqrt(3)*400*cos(-120*pi/180)
  U_v Im = Real $ sqrt(2)/sqrt(3)*400*sin(-120*pi/180)
  U_w Re = Real $ sqrt(2)/sqrt(3)*400*cos(120*pi/180)
  U_w Im = Real $ sqrt(2)/sqrt(3)*400*sin(120*pi/180)
End

Body Force 2
  Mesh Rotate 3 = Real $ r_angle
End

{rotor_bodies}

Body {rotor_bars + 1}
  Name = U_plus
  Equation = 1
  Material = 4
End

Body {rotor_bars + 2}
  Name = W_minus
  Equation = 1
  Material = 4
End

Body {rotor_bars + 3}
  Name = V_plus
  Equation = 1
  Material = 4
End

Body {rotor_bars + 4}
  Name = StatorIron
  Equation = 1
  Material = 2
End

Body {rotor_bars + 5}
  Name = StatorWedges
  Equation = 1
  Material = 1
End

Body {rotor_bars + 6}
  Name = StatorAirgap
  Equation = 1
  Material = 1
End

Body {rotor_bars + 7}
  Name = RotorIron
  Equation = 1
  Material = 2
  Body Force = 2
  Torque Groups = Integer 1
End

Body {rotor_bars + 8}
  Name = RotorAirgap
  Equation = 1
  Material = 1
  Body Force = 2
  R Inner = Real 0.0620
  R Outer = Real 0.0625
End

include "cage/cage.definitions"

Component 11
  Name = String Uplus
  Body = Integer 11
  Coil Type = String Stranded
  Number of Turns = Real $ Nph/2
  Resistance = Real $ Rs
End

Component 12
  Name = String Vplus
  Body = Integer 13
  Coil Type = String Stranded
  Number of Turns = Real $ Nph/2
  Resistance = Real $ Rs
End

Component 13
  Name = String Wminus
  Body = Integer 12
  Coil Type = String Stranded
  Number of Turns = Real $ Nph/2
  Resistance = Real $ Rs
End

Equation 1 :: Active Solvers(2) = 2 3

Solver 1
  Exec Solver = Always
  Equation = MgDyn2D
  Variable = A
  Procedure = "MagnetoDynamics2D" "MagnetoDynamics2D"
End

Solver 2
  Exec Solver = Always
  Equation = CalcFields
  Potential Variable = "A"
  Procedure = "MagnetoDynamics" "MagnetoDynamicsCalcFields"
  Calculate Current Density = Logical True
  Calculate Magnetic Vector Potential = Logical True
End

Boundary Condition 1
  Name = OuterStator
  A = Real 0
End

Boundary Condition 2
  Name = StatorRight
  Mortar BC = Integer 3
  Mortar BC Static = Logical True
  Anti Radial Projector = Logical True
  Galerkin Projector = Logical True
End

Boundary Condition 3
  Name = StatorLeft
End

Boundary Condition 4
  Name = Sliding_Stator
  Mortar BC = Integer 5
  Anti Rotational Projector = Logical True
  Galerkin Projector = Logical True
End

Boundary Condition 5
  Name = InnerRotor
  A = Real 0
End

Boundary Condition 6
  Name = RotorRight
  Mortar BC = Integer 7
  Mortar BC Static = Logical True
  Anti Radial Projector = Logical True
  Galerkin Projector = Logical True
End

Boundary Condition 7
  Name = RotorLeft
End

Boundary Condition 8
  Name = Sliding_Rotor
End
'''

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


__all__ = ["generate_harmonic_sif"]
