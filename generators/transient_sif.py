from __future__ import annotations

from pathlib import Path


def generate_transient_sif(path: str | Path, rotor_bars: int = 40) -> None:
    rotor_bodies = "\n".join(
        f'''Body {i}
  Name = Bar{i}
  Equation = 1
  Material = 3
  Body Force = 7
  Torque Groups = Integer 1
End
''' for i in range(1, rotor_bars + 1)
    )

    content = f'''include transient_params.dat

Header
  Mesh DB "im"
  Results Directory "results"
  Include Path "materials"
End

Simulation
  Max Output Level = 3
  Coordinate System = Cartesian 2D
  Coordinate Scaling = 0.001
  Circuit Model Depth = Real $ l
  Simulation Type = Transient
  Timestepping Method = BDF
  BDF Order = 2
  Output Intervals = 1
  Timestep Sizes = $ 1/f/15
  Timestep Intervals = $ 25*15
  Use Mesh Names = Logical True
End

Material 1
  Relative Permeability = 1
  Electric Conductivity = 0
End

Material 2
  Name = "Iron"
  INCLUDE el_steel_M800_65A
  Electric Conductivity = 0
End

Material 3
  Relative Permeability = 1
  Electric Conductivity = 24e6
End

Material 4
  Relative Permeability = 1
  Electric Conductivity = 48e6
End

Body Force 1
  Name = "Circuit"
  U_u = Variable time
    Real MATC "400*sqrt(2)/sqrt(3)*sin(tx(0)*2*pi*f)"
  U_v = Variable time
    Real MATC "400*sqrt(2)/sqrt(3)*sin(tx(0)*2*pi*f-2*pi/3)"
  U_w = Variable time
    Real MATC "400*sqrt(2)/sqrt(3)*sin(tx(0)*2*pi*f+2*pi/3)"
End

Body Force 7
  Mesh Rotate 3 = Variable time
    Real MATC "180/pi*2*pi*f/pp*(1-slip)*tx"
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
  Body Force = 7
  Torque Groups = Integer 1
End

Body {rotor_bars + 8}
  Name = RotorAirgap
  Equation = 1
  Material = 1
  Body Force = 7
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

Equation 1 :: Active Solvers(3) = 2 3 4

Solver 1
  Exec Solver = Before timestep
  Equation = MeshDeform
  Procedure = "RigidMeshMapper" "RigidMeshMapper"
End

Solver 2
  Exec Solver = Always
  Equation = Circuits
  Variable = X
  Procedure = "CircuitsAndDynamics" "CircuitsAndDynamics"
  No Matrix = Logical True
End

Solver 3
  Exec Solver = Always
  Equation = MgDyn2D
  Variable = A
  Procedure = "MagnetoDynamics2D" "MagnetoDynamics2D"
  Nonlinear System Convergence Tolerance = 1e-6
  Nonlinear System Max Iterations = 20
  Linear System Solver = Iterative
  Linear System Iterative Method = GCR
  Linear System Preconditioning = ILU4
  Linear System Max Iterations = 1500
  Linear System Convergence Tolerance = 1e-7
End

Solver 4
  Exec Solver = Always
  Equation = CalcFields
  Potential Variable = "A"
  Procedure = "MagnetoDynamics" "MagnetoDynamicsCalcFields"
  Calculate Nodal Forces = Logical True
  Calculate Magnetic Torque = Logical True
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
  Mortar BC = Integer 8
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


__all__ = ["generate_transient_sif"]
