# Elmer_IM2D_cases

This fork keeps the original project intact while adding a parameterized full-machine branch for 2D induction-machine modelling.

The original upstream repo models a single-pole sector of an induction machine. In the full machine, the number of active rotor bars and stator coil connections increases, so the case definition must be generated from the actual total tooth counts instead of being hardcoded to a reduced sector.

This branch adds a generator that can create a full-machine case for:
- one-pole sector: N_ss = Qs/4, N_rs = Qr/4
- half-machine sector: N_ss = Qs/2, N_rs = Qr/2
- full-machine: N_ss = Qs, N_rs = Qr

Generator:
- scripts/generate_full_machine_case.py

Generated full-machine example:
- IM_full_machine/

Usage:
  python scripts/generate_full_machine_case.py --qs 48 --qr 40 --ns 48 --nr 40

The generated files keep the same Elmer structure but expand the rotor-body and stator-connection definitions to the actual machine size.
