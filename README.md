# Elmer_IM2D_cases

This fork is for experimentation and code changes without modifying the original repository.

The original project is a 2D induction-machine case library built around a single-pole sector model. The geometry scripts have been generalized here so the same framework can be used for sector fractions of 1/4, 1/2, and 1/1 of the full stator/rotor tooth count.

The relevant geometry files are:
- IM_one_pole/gmsh/im_stator.geo
- IM_one_pole/gmsh/im_rotor.geo

The code supports the following configurations:
- N_ss = Qs/4 (one pole)
- N_ss = Qs/2 (half-machine sector)
- N_ss = Qs (full machine)
- N_rs = Qr/4 (one pole)
- N_rs = Qr/2 (half-machine sector)
- N_rs = Qr (full machine)

The repo privacy setting must be changed in the GitHub UI/API separately; it is not controlled by the code in this branch.
