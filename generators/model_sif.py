from __future__ import annotations

from pathlib import Path


def generate_model_sif(path: str | Path, rotor_bars: int = 40) -> None:
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

    content = f'''Header
  Mesh DB "im"
  Results Directory "results"
  Include Path "materials"
End

Simulation
  Max Output Level = 3
  Coordinate System = Cartesian
  Coordinate Scaling = 0.001
  Simulation Type = Steady
  Use Mesh Names = Logical True
End

Material 1
  Relative Permeability = 1
End

Material 2
  Name = "Iron"
  INCLUDE el_steel_M800_65A
End

Body Force 1
  Mesh Rotate 3 = Real MATC "10"
End

Body Force 2
  Current Density = 3e6
End

Body Force 3
  Current Density = -1.5e6
End

Body Force 4
  Current Density = 1.5e6
End

{rotor_bodies}

Body {rotor_bars + 1}
  Name = U_plus
  Equation = 1
  Material = 1
  Body Force = 2
End

Body {rotor_bars + 2}
  Name = W_minus
  Equation = 1
  Material = 1
  Body Force = 4
End

Body {rotor_bars + 3}
  Name = V_plus
  Equation = 1
  Material = 1
  Body Force = 3
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
  Body Force = 1
End

Body {rotor_bars + 8}
  Name = RotorAirgap
  Equation = 1
  Material = 1
  Body Force = 1
End

Equation 1 :: Active Solvers(2) = 2 3

Solver 1
  Exec Solver = Before simulation
  Equation = MeshDeform
  Procedure = "RigidMeshMapper" "RigidMeshMapper"
End

Solver 2
  Exec Solver = Always
  Equation = MgDyn2D
  Variable = A
  Procedure = "MagnetoDynamics2D" "MagnetoDynamics2D"
  Nonlinear System Convergence Tolerance = 1.0e-4
  Nonlinear System Max Iterations = 30
  Linear System Solver = Direct
  Linear System Iterative Method = MUMPS
End

Solver 3
  Exec Solver = Always
  Equation = CalcFields
  Potential Variable = "A"
  Procedure = "MagnetoDynamics" "MagnetoDynamicsCalcFields"
  Calculate Current Density = Logical True
  Calculate Magnetic Vector Potential = Logical True
End

Solver 4
  Exec Solver = after simulation
  Equation = "ResultOutput"
  Procedure = "ResultOutputSolve" "ResultOutputSolver"
  Output File Name = case
  Output Directory = results
  Save Geometry Ids = Logical True
  Vtu Format = Logical True
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
  Name = Sliding_Rotor
End

Boundary Condition 6
  Name = InnerRotor
  A = Real 0
End

Boundary Condition 7
  Name = RotorRight
  Mortar BC = Integer 8
  Mortar BC Static = Logical True
  Anti Radial Projector = Logical True
  Galerkin Projector = Logical True
End

Boundary Condition 8
  Name = RotorLeft
End
'''

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


__all__ = ["generate_model_sif"]
