from __future__ import annotations

from pathlib import Path


def generate_rotor_geo(path: str | Path, qr: int = 40, nr: int = 40) -> None:
    geo = f'''// Generated rotor geometry for full-machine or sector cases
Geometry.AutoCoherence = 0;
Mesh.Light = 0;

Qr = {qr};
N_rs = {nr};

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
    dP = newp;
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
      Rotate {{0,0,1},{0,0,0}, 2*Pi*i/Qr+2*Pi/Qr/2} {Point{{t}};}
    EndFor
    If (half==1)
      For t In {{dP+0:dP+13}}
        Symmetry {{Cos(2*Pi*i/Qr+2*Pi/Qr/2),Sin(2*Pi*i/Qr+2*Pi/Qr/2),0,0}} {Point{{t}};}
      EndFor
    EndIf
    dR = newl-1;
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

Physical Surface("RotorIron") = {{RotorIron_[]}};
Physical Surface("RotorAirgap") = {{RotorAirgapLayer_[]}};
Physical Line("InnerRotor") = {{InnerRotor_[]}};
Physical Line("Sliding_Rotor") = {{SlidingR_[]}};
Coherence;
Mesh 2;
'''
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(geo, encoding="utf-8")


__all__ = ["generate_rotor_geo"]
