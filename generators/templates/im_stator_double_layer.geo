//Mesh density
m_coarse = 20;
m_normal = 12;
m_gap = 0.55;
m_sl_top = 7;
m_sl_bot = 1.5;
m_s_out = 12;

//Stator
Qs = 24; // number of stator teeth
N_ss = 6;

//Winding
qq = 2;        // slots per pole per phase (belt width)
y_p = 5;       // coil pitch in slots (short pitch, full pitch = 3*qq = 6)

//Main Stator parameters
R_sin = 35.6; // inner stator radius
R_sout = 60; // outer stator radius
R_g = 35.41; // middle of the air gap radius

//Slot dimensions
b_5 = 7.75;
b_1 = 3.0;
h_1 = 0.8;
h_2 = 0.8;
b_4 = 5;
h_5 = 12;
h_w0 = 0.5;    // height of the wedge region above h_2 (bottom of winding)

//offset for the curvature of the slot opening in the gap
s = R_sin - Sqrt(R_sin^2-(b_1/2)^2);

//---- Equal-area split of the winding (per half slot) ----
// half-width of the winding grows linearly from a=b_4/2 (bottom) to b_5/2 (top of the straight part)
h_w = h_5 - h_w0;                              // height of straight (trapezoid) part
a_w = b_4/2;
k_w = (b_5/2 - b_4/2)/h_w;                     // d(half-width)/dy
A_half = h_w*(b_4/2+b_5/2)/2 + Pi*(b_5/2)^2/4; // trapezoid + quarter circle
// solve a_w*h + k_w*h^2/2 = A_half/2 for the height h_m of the dividing line
h_m = (-a_w + Sqrt(a_w^2 + k_w*A_half))/k_w;
w_m = a_w + k_w*h_m;                           // half-width at the dividing line

Geometry.AutoCoherence = 0;

//build stator slots
For i In {0:N_ss-1}
    //build two halfs
    For half In {0:1}
        //Points definitions
        //points of one half
        dP=newp;
        Point(dP+0) = {0,0,0,m_coarse};
        //right toothtip points
        Point(dP+1) = {b_1/2, R_sin-s, 0, 2*m_gap};
        Point(dP+2) = {b_1/2, R_sin-s+h_1, 0, m_sl_bot};
        //center of the top circle
        Point(dP+3) = {0, R_sin-s+h_1+h_2+h_5, 0, m_sl_top};
        //h2-b4 bottom teeth point
        Point(dP+4) = {b_4/2, R_sin-s+h_1+h_2, 0, m_sl_bot};
        //h5-b5 top teeth point
        Point(dP+5) = {b_5/2, R_sin-s+h_1+h_2+h_5, 0, m_sl_top};
        // point of lower winding
        Point(dP+6) = {b_4/2, R_sin-s+h_1+h_2+h_w0, 0, m_sl_bot/2};
        // central point of lower winding
        Point(dP+7) = {0, R_sin-s+h_1+h_2+h_w0, 0, m_sl_bot};
        // top slot point
        Point(dP+8) = {0, R_sin-s+h_1+h_2+h_5+b_5/2, 0, m_sl_top};
        // outer stator sector
        Point(dP+9) = {R_sout*Sin(Pi/Qs), R_sout*Cos(Pi/Qs), 0, m_s_out};
        // outer stator center
        Point(dP+10) = {0, R_sout, 0, m_s_out};
        // inner stator sector
        Point(dP+11) = {R_sin*Sin(Pi/Qs), R_sin*Cos(Pi/Qs), 0, 2.5*m_gap};
        // sliding sector
        Point(dP+12) = {R_g*Sin(Pi/Qs), R_g*Cos(Pi/Qs), 0, 2.4*m_gap};
        //inner stator center
        Point(dP+13) = {0, R_sin, 0, 1.5*m_gap};
        //sliding center
        Point(dP+14) = {0, R_g, 0, 1.5*m_gap};
        // layer divider: point on the slanted slot side
        Point(dP+15) = {w_m, R_sin-s+h_1+h_2+h_w0+h_m, 0, m_sl_bot};
        // layer divider: point on the slot centre line
        Point(dP+16) = {0, R_sin-s+h_1+h_2+h_w0+h_m, 0, m_sl_bot};

        // rotate the built points to the i-th slot position
        For t In {dP+0:dP+16}
            Rotate {{0,0,1},{0,0,0}, 2*Pi*i/Qs+2*Pi/Qs/2} {Point{t};}
        EndFor

        If (half==1) //second half
            For t In {dP+0:dP+16}
                Symmetry {Cos(2*Pi*i/Qs+2*Pi/Qs/2),Sin(2*Pi*i/Qs+2*Pi/Qs/2),0,0} {Point{t};}
            EndFor
        EndIf

        //Lines definitions
        dR=newl-1;
        //vertical tooth tip line
        Line(dR+1) = {dP+1,dP+2};
        //line from tooth tip arc to start of the winding
        Line(dR+2) = {dP+4,dP+6};
        //slot side, lower part (up to layer divider)
        Line(dR+3) = {dP+6,dP+15};
        //horizontal winding bottom
        Line(dR+4) = {dP+6,dP+7};
        //arc toothtip - side
        Line(dR+5) = {dP+2,dP+4};
        //arc top of the slot-side
        Circle(dR+6) = {dP+5,dP+3,dP+8};
        //sliding
        Circle(dR+7) = {dP+12,dP+0,dP+14};
        //slot opening arc
        Circle(dR+8) = {dP+11,dP+0,dP+1};
        //arc inner teeth surface
        Circle(dR+9) = {dP+1,dP+0,dP+13};
        //outer stator
        Circle(dR+10) = {dP+9,dP+0,dP+10};
        //vertical central slot opening
        Line(dR+11) = {dP+13,dP+7};
        //slot centre line, lower part
        Line(dR+12) = {dP+7,dP+16};
        //vertical from top of the slot to the stator outer
        Line(dR+13) = {dP+8,dP+10};
        //sector border via steel
        Line(dR+14) = {dP+11,dP+9};
        //sector border via airgap
        Line(dR+15) = {dP+12,dP+11};
        //vertical sector center via gap
        Line(dR+16) = {dP+14,dP+13};
        //slot side, upper part
        Line(dR+17) = {dP+15,dP+5};
        //slot centre line, upper part
        Line(dR+18) = {dP+16,dP+8};
        //layer divider (horizontal)
        Line(dR+19) = {dP+15,dP+16};

        //filling the lists for boundaries
        OuterStator_[] += dR+10;
        StatorBoundary_[] += {dR+10,dR+6,dR+3,dR+17,dR+2,dR+5,dR+1,dR+8};
        Sliding_[] += {dR+7};
        //Periodic boundary
        If (Qs != N_ss)
            //right boundary
            If (i==0 && half==0)
                StatorPeriod_Right_[] = {dR+14,dR+15};
            EndIf
            //left boundary
            If (i == N_ss-1 && half==1)
                StatorPeriod_Left_[] = {dR+14,dR+15};
            EndIf
        EndIf

        //if mirrored, then the lines order is reversed
        //direction is important defining the Line Loops
        rev = (half ? -1 : 1);
        //lower layer (airgap side)
        Line Loop(newll) = {dR+12,-dR-19,-dR-3,dR+4};
        dH = news; Plane Surface(news) = -rev*{newll-1};
        StatorCondBot_[] += dH;
        //upper layer (yoke side)
        Line Loop(newll) = {dR+18,-dR-6,-dR-17,dR+19};
        dH = news; Plane Surface(news) = -rev*{newll-1};
        StatorCondTop_[] += dH;
        //surface of the stator iron
        Line Loop(newll) = {dR+1,dR+5,dR+2,dR+3,dR+17,dR+6,dR+13,-dR-10,-dR-14,dR+8};
        dH = news; Plane Surface(news) = -rev*{newll-1};
        StatorIron_[] += dH;
        //wedges
        Line Loop(newll) = {dR+11,-dR-4,-dR-2,-dR-5,-dR-1,dR+9};
        dH = news; Plane Surface(news) = -rev*{newll-1};
        StatorWedge_[] += dH;
        //airgap stator
        Line Loop(newll) = {-dR-16,-dR-7,dR+15,dR+8,dR+9};
        dH = news; Plane Surface(news) = rev*{newll-1};
        StatorAirgapLayer_[] += dH;

    EndFor
EndFor

//Assigning StatorConductors to phase Regions (double layer, short pitch y_p)
// Belt index: 0:U+  1:W-  2:V+  3:U-  4:W+  5:V-
// Upper layer of slot n carries the "nominal" belt of slot n.
// Lower layer of slot n carries the return side of the coil whose upper side is in slot n-y_p,
// i.e. that belt reversed (belt index + 3).
// Each slot has 2 surfaces per layer (left/right half): indices 2*n and 2*n+1.
For f In {0:5}
    Con[]={};
    For sl In {0:N_ss-1}
        bt = Fmod(Floor(sl/qq),6);
        bb = Fmod(Floor((sl-y_p+Qs)/qq)+3,6);
        If (bt == f)
            Con[] += StatorCondTop_[{2*sl, 2*sl+1}];
        EndIf
        If (bb == f)
            Con[] += StatorCondBot_[{2*sl, 2*sl+1}];
        EndIf
    EndFor
    //color the phase and assign to a physical region
    If (#Con[] > 0)
        If (f == 0)
            Color Red {Surface{Con[]};}
            Physical Surface("U_plus") = {Con[]};
        EndIf
        If (f == 1)
            Color SpringGreen {Surface{Con[]};}
            Physical Surface("W_minus") = {Con[]};
        EndIf
        If (f == 2)
            Color Gold {Surface{Con[]};}
            Physical Surface("V_plus") = {Con[]};
        EndIf
        If (f == 3)
            Color Pink {Surface{Con[]};}
            Physical Surface("U_minus") = {Con[]};
        EndIf
        If (f == 4)
            Color ForestGreen {Surface{Con[]};}
            Physical Surface("W_plus") = {Con[]};
        EndIf
        If (f == 5)
            Color PaleGoldenrod {Surface{Con[]};}
            Physical Surface("V_minus") = {Con[]};
        EndIf
    EndIf
EndFor

Physical Surface("StatorIron") = {StatorIron_[]};
Physical Surface("StatorWedges") = {StatorWedge_[]};
Physical Surface("StatorAirgap") = {StatorAirgapLayer_[]};
Color SteelBlue {Surface{StatorIron_[]};}
Color Black {Surface{StatorWedge_[]};}
Color SkyBlue {Surface{StatorAirgapLayer_[]};}

Physical Line("OuterStator") = {OuterStator_[]};
Physical Line("StatorRight") = {StatorPeriod_Right_[]};
Physical Line("StatorLeft") = {StatorPeriod_Left_[]};
Physical Line("Sliding_Stator") = {Sliding_[]};

Coherence;
show_stator[] = CombinedBoundary{Surface{StatorIron_[]};};
show_stator[] +=
CombinedBoundary{Surface{StatorWedge_[],StatorAirgapLayer_[]};};
Hide { Point{ Point '*' }; }
Hide { Line{ Line '*' }; }
Show { Line{ show_stator[] }; }
Mesh 2;