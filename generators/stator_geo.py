from __future__ import annotations

from pathlib import Path


def generate_stator_geo(path: str | Path, qs: int = 48, ns: int = 48) -> None:
    geo = f'''// Generated stator geometry for full-machine or sector cases
Geometry.AutoCoherence = 0;

Qs = {qs};
N_ss = {ns};

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
    dP = newp;
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
      Rotate {{0,0,1},{0,0,0}, 2*Pi*i/Qs+2*Pi/Qs/2} {Point{{t}};}
    EndFor
    If (half==1)
      For t In {{dP+0:dP+14}}
        Symmetry {{Cos(2*Pi*i/Qs+2*Pi/Qs/2),Sin(2*Pi*i/Qs+2*Pi/Qs/2),0,0}} {Point{{t}};}
      EndFor
    EndIf
    dR = newl-1;
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

Physical Surface("StatorIron") = {{StatorIron_[]}};
Physical Surface("StatorWedges") = {{StatorWedge_[]}};
Physical Surface("StatorAirgap") = {{StatorAirgapLayer_[]}};
Physical Line("OuterStator") = {{OuterStator_[]}};
Physical Line("Sliding_Stator") = {{Sliding_[]}};
Coherence;
Mesh 2;
'''
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(geo, encoding="utf-8")


__all__ = ["generate_stator_geo"]
