#!/usr/bin/env python3
"""Generate a full-machine Elmer case from total tooth counts.

This script creates the .geo and .sif files for a full machine (or any
sector fraction), while avoiding the hardcoded 10-bar / 3-phase single-pole
assumptions used in the reduced-sector examples.
"""

from pathlib import Path
from textwrap import dedent


def write_model_sif(path: Path, nr: int, ns: int, qrs: int, qss: int) -> None:
    rotor_bodies = []
    for i in range(1, nr + 1):
        rotor_bodies.append(dedent(f"""
        Body {i}
          Name = Bar{i}
          Equation = 1
          Material = 3
          Body Force = 7
          Torque Groups = Integer 1
        End
        """))

    bar_block = "\n".join(rotor_bodies)

    phase_bodies = [
        ("U_plus", 11, "Body Force = 2"),
        ("W_minus", 12, "Body Force = 4"),
        ("V_plus", 13, "Body Force = 3"),
    ]
    phase_block = "\n".join(
        dedent(f"""
        Body {body_id}
          Name = {name}
          Equation = 1
          Material = 4
          {force}
        End
        """)
        for name, body_id, force in phase_bodies
    )

    model = dedent(f"""
    Header
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

    {bar_block}

    {phase_block}

    Body {nr + 11}
      Name = StatorIron
      Equation = 1
      Material = 2
    End

    Body {nr + 12}
      Name = StatorWedges
      Equation = 1
      Material = 1
    End

    Body {nr + 13}
      Name = StatorAirgap
      Equation = 1
      Material = 1
    End

    Body {nr + 14}
      Name = RotorIron
      Equation = 1
      Material = 2
      Body Force = 1
    End

    Body {nr + 15}
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
    """).strip() + "\n"

    path.write_text(model, encoding='utf-8')


def write_transient_sif(path: Path, nr: int) -> None:
    rotor_bodies = []
    for i in range(1, nr + 1):
        rotor_bodies.append(dedent(f"""
        Body {i}
          Name = Bar{i}
          Equation = 1
          Material = 3
          Body Force = 7
          Torque Groups = Integer 1
        End
        """))

    phase_bodies = [
        ("U_plus", 11, "Body Force = 2"),
        ("W_minus", 12, "Body Force = 4"),
        ("V_plus", 13, "Body Force = 3"),
    ]
    phase_block = "\n".join(
        dedent(f"""
        Body {body_id}
          Name = {name}
          Equation = 1
          Material = 4
          {force}
        End
        """)
        for name, body_id, force in phase_bodies
    )

    block = dedent(f"""
    include transient_params.dat

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

    {''.join(rotor_bodies)}

    {phase_block}

    Body {nr + 11}
      Name = StatorIron
      Equation = 1
      Material = 2
    End

    Body {nr + 12}
      Name = StatorWedges
      Equation = 1
      Material = 1
    End

    Body {nr + 13}
      Name = StatorAirgap
      Equation = 1
      Material = 1
    End

    Body {nr + 14}
      Name = RotorIron
      Equation = 1
      Material = 2
      Body Force = 7
      Torque Groups = Integer 1
    End

    Body {nr + 15}
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
    """).strip() + "\n"

    path.write_text(block, encoding='utf-8')


def write_geo(path: Path, qs: int, qr: int, ns: int, nr: int) -> None:
    geo = dedent(f"""
    Geometry.AutoCoherence = 0;
    Mesh.Light = 0;

    Qs = {qs};
    Qr = {qr};
    N_ss = {ns};
    N_rs = {nr};

    // This branch supports full-machine generation by setting N_ss = Qs and N_rs = Qr.
    // For reduced sectors, use N_ss = Qs/2 or Qs/4 and N_rs = Qr/2 or Qr/4.

    // ----- stator geometry -----
    R_sin = 62.5;
    R_sout = 110;
    R_g = 62.25;
    b_5 = 6.8;
    b_1 = 2.8;
    h_1 = 0.7;
    h_2 = 0.2;
    b_4 = 4;
    h_5 = 24;
    m_coarse = 20;
    m_normal = 12;
    m_gap = 0.55;
    m_sl_top = 7;
    m_sl_bot = 2;
    m_s_out = 12;
    s = R_sin-Sqrt(R_sin^2-(b_1/2)^2);

    For i In {{0:N_ss-1}}
      For half In {{0:1}}
        dP=newp;
        Point(dP+0)  = {{0,0,0,m_coarse}};
        Point(dP+1)  = {{b_1/2, R_sin-s, 0, 2*m_gap}};
        Point(dP+2)  = {{b_1/2, R_sin-s+h_1, 0, m_sl_bot}};
        Point(dP+3)  = {{0, R_sin-s+h_1+h_2+h_5, 0, m_sl_top}};
        Point(dP+4)  = {{b_4/2, R_sin-s+h_1+h_2, 0, m_sl_bot}};
        Point(dP+5)  = {{b_5/2, R_sin-s+h_1+h_2+h_5, 0, m_sl_top}};
        Point(dP+6)  = {{b_4/2, R_sin-s+h_1+h_2+0.5, 0, m_sl_bot/2}};
        Point(dP+7)  = {{0, R_sin-s+h_1+h_2+0.5, 0, m_sl_bot}};
        Point(dP+8)  = {{0, R_sin-s+h_1+h_2+h_5+b_5/2, 0, m_sl_top}};
        Point(dP+9) = {{R_sout*Sin(Pi/Qs), R_sout*Cos(Pi/Qs), 0, m_s_out}};
        Point(dP+10) = {{0, R_sout, 0, m_s_out}};
        Point(dP+11) = {{R_sin*Sin(Pi/Qs), R_sin*Cos(Pi/Qs), 0, 2.5*m_gap}};
        Point(dP+12) = {{R_g*Sin(Pi/Qs), R_g*Cos(Pi/Qs), 0, 2.4*m_gap}};
        Point(dP+13) = {{0, R_sin, 0, 1.5*m_gap}};
        Point(dP+14) = {{0, R_g, 0, 1.5*m_gap}};
        For t In {{dP+0:dP+14}}
          Rotate {{0,0,1}},{{0,0,0}},{{2*Pi*i/Qs+2*Pi/Qs/2}} {{Point{{t}};}}
        EndFor
        If (half==1)
          For t In {{dP+0:dP+14}}
            Symmetry {{Cos(2*Pi*i/Qs+2*Pi/Qs/2),Sin(2*Pi*i/Qs+2*Pi/Qs/2),0,0}} {{ Point{{t}}; }}
          EndFor
        EndIf
        dR=newl-1;
        Line(dR+1) = {{dP+1,dP+2}};
        Line(dR+2) = {{dP+4,dP+6}};
        Line(dR+3) = {{dP+6,dP+5}};
        Line(dR+4) = {{dP+6,dP+7}};
        Line(dR+5) = {{dP+2,dP+4}};
        Circle(dR+6) = {{dP+5,dP+3,dP+8}};
        Circle(dR+7) = {{dP+12,dP+0,dP+14}};
        Circle(dR+8) = {{dP+11,dP+0,dP+1}};
        Circle(dR+9) = {{dP+1,dP+0,dP+13}};
        Circle(dR+10) = {{dP+9,dP+0,dP+10}};
        Line(dR+11) = {{dP+13,dP+7}};
        Line(dR+12) = {{dP+7,dP+8}};
        Line(dR+13) = {{dP+8,dP+10}};
        Line(dR+14) = {{dP+11,dP+9}};
        Line(dR+15) = {{dP+12,dP+11}};
        Line(dR+16) = {{dP+14,dP+13}};
        OuterStator_[] += dR+10;
        StatorBoundary_[] += {{dR+10,dR+6,dR+3,dR+2,dR+5,dR+1,dR+8}};
        Sliding_[] += {{dR+7}};
        rev = (half ? -1 : 1);
        Line Loop(newll) = {{dR+12,-dR-6,-dR-3,dR+4}};
        dH = news; Plane Surface(news) = -rev*{{newll-1}};
        StatorConductor_[] += dH;
        Line Loop(newll) = {{dR+1,dR+5,dR+2,dR+3,dR+6,dR+13,-dR-10,-dR-14,dR+8}};
        dH = news; Plane Surface(news) = -rev*{{newll-1}};
        StatorIron_[] += dH;
        Line Loop(newll) = {{dR+11,-dR-4,-dR-2,-dR-5,-dR-1,dR+9}};
        dH = news; Plane Surface(news) = -rev*{{newll-1}};
        StatorWedge_[] += dH;
        Line Loop(newll) = {{-dR-16,-dR-7,dR+15,dR+8,dR+9}};
        dH = news; Plane Surface(news) = rev*{{newll-1}};
        StatorAirgapLayer_[] += dH;
      EndFor
    EndFor

    // ----- rotor geometry -----
    R_rin = 27;
    R_rout = 62;
    R_g = 62.25;
    b_1 = 1;
    h_1 = 0.4;
    b_4 = 4.4;
    b_5 = 2;
    h_5 = 12;
    m_coarse = 10;
    m_normal = 8;
    m_gap = 0.5;
    m_sl_bot = 4;
    m_sl_top = 1;
    m_r_in = 10;
    s = R_rout-Sqrt((R_rout)^2-(b_1/2)^2);
    s2 = b_4/2-Sqrt((b_4/2)^2-(b_1/2)^2);

    For i In {{0:N_rs-1}}
      For half In {{0:1}}
        dP=newp;
        Point(dP+0)  = {{0,0,0,m_coarse}};
        Point(dP+1)  = {{b_1/2, R_rout-s, 0, 1.4*m_gap}};
        Point(dP+2)  = {{b_1/2, R_rout-h_1-s2, 0, m_sl_top}};
        Point(dP+3)  = {{0, R_rout-h_1-b_4/2-h_5, 0, m_sl_bot}};
        Point(dP+4)  = {{b_4/2, R_rout-h_1-b_4/2, 0, 2*m_sl_top}};
        Point(dP+5)  = {{b_5/2, R_rout-h_1-b_4/2-h_5, 0, m_sl_bot}};
        Point(dP+6)  = {{0, R_rout-h_1-b_4/2, 0, m_sl_top}};
        Point(dP+7)  = {{0, R_rout-h_1-b_4/2-h_5-b_5/2, 0, m_sl_bot}};
        Point(dP+8) = {{R_rin*Sin(Pi/Qr), R_rin*Cos(Pi/Qr), 0, m_r_in}};
        Point(dP+9) = {{0, R_rin, 0, m_r_in}};
        Point(dP+10) = {{R_rout*Sin(Pi/Qr), R_rout*Cos(Pi/Qr), 0, 2.5*m_gap}};
        Point(dP+11) = {{R_g*Sin(Pi/Qr), R_g*Cos(Pi/Qr), 0, 2.8*m_gap}};
        Point(dP+12) = {{0, R_rout, 0, 1.5*m_gap}};
        Point(dP+13) = {{0, R_g, 0, 1.4*m_gap}};
        For t In {{dP+0:dP+13}}
          Rotate {{0,0,1},{0,0,0}, 2*Pi*i/Qr+2*Pi/Qr/2} {{Point{{t}};}}
        EndFor
        If (half==1)
          For t In {{dP+0:dP+13}}
            Symmetry {{Cos(2*Pi*i/Qr+2*Pi/Qr/2),Sin(2*Pi*i/Qr+2*Pi/Qr/2),0,0}} {{ Point{{t}}; }}
          EndFor
        EndIf
        dR=newl-1;
        Line(dR+1) = {{dP+1,dP+2}};
        Circle(dR+2) = {{dP+2,dP+6,dP+4}};
        Line(dR+3) = {{dP+4,dP+5}};
        Circle(dR+4) = {{dP+5,dP+3,dP+7}};
        Circle(dR+5) = {{dP+11,dP+0,dP+13}};
        Circle(dR+6) = {{dP+10,dP+0,dP+1}};
        Circle(dR+7) = {{dP+1,dP+0,dP+12}};
        Circle(dR+8) = {{dP+8,dP+0,dP+9}};
        Line(dR+9) = {{dP+12,dP+7}};
        Line(dR+10) = {{dP+7,dP+9}};
        Line(dR+11) = {{dP+10,dP+8}};
        Line(dR+12) = {{dP+11,dP+10}};
        Line(dR+13) = {{dP+13,dP+12}};
        InnerRotor_[] += dR+8;
        RotorBoundary_[] += {{dR+8,dR+4,dR+3,dR+2,dR+1,dR+6}};
        SlidingR_[] += {{dR+5}};
        rev = (half ? -1 : 1);
        Line Loop(newll) = {{dR+9,-dR-4,-dR-3,-dR-2,-dR-1,dR+7}};
        dH = news; Plane Surface(news) = -rev*{{newll-1}};
        RotorConductor_[] += dH;
        Line Loop(newll) = {{dR+1,dR+2,dR+3,dR+4,dR+10,-dR-8,-dR-11,dR+6}};
        dH = news; Plane Surface(news) = -rev*{{newll-1}};
        RotorIron_[] += dH;
        Line Loop(newll) = {{-dR-13,-dR-5,dR+12,dR+6,dR+7}};
        dH = news; Plane Surface(news) = rev*{{newll-1}};
        RotorAirgapLayer_[] += dH;
      EndFor
    EndFor

    For i In {{0:N_rs-1}}
      Physical Surface(Sprintf("Bar%d", i+1)) = {{RotorConductor_[{{2*i,2*i+1}}]}};
    EndFor
    Physical Surface("RotorIron") = {{RotorIron_[]}};
    Physical Surface("RotorAirgap") = {{RotorAirgapLayer_[]}};
    Physical Line("InnerRotor") = {{InnerRotor_[]}};
    Physical Line("Sliding_Rotor") = {{SlidingR_[]}};
    Physical Line("OuterStator") = {{OuterStator_[]}};
    If (N_ss < Qs)
      Physical Line("StatorRight") = {{StatorPeriod_Right_[]}};
      Physical Line("StatorLeft") = {{StatorPeriod_Left_[]}};
    EndIf
    If (N_rs < Qr)
      Physical Line("RotorRight") = {{RotorPeriod_Right_[]}};
      Physical Line("RotorLeft") = {{RotorPeriod_Left_[]}};
    EndIf
    Coherence;
    Mesh 2;
    """).strip() + "\n"

    path.write_text(geo, encoding='utf-8')


def main() -> None:
    # Default values correspond to the original example machine.
    qs = 48
    qr = 40
    ns = 48
    nr = 40
    out_dir = Path('IM_full_machine')
    out_dir.mkdir(exist_ok=True)
    (out_dir / 'gmsh').mkdir(exist_ok=True)
    write_geo(out_dir / 'gmsh' / 'im_stator.geo', qs, qr, ns, nr)
    write_geo(out_dir / 'gmsh' / 'im_rotor.geo', qs, qr, ns, nr)
    write_model_sif(out_dir / 'model.sif', nr, ns, qr, qs)
    write_transient_sif(out_dir / 'transient.sif', nr)


if __name__ == '__main__':
    main()
