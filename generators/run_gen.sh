#!/bin/sh

rm -rf results im ELMERSOLVER_STARTINFO


gmsh="/home/nakic/Downloads/gmsh-4.15.2-Linux64/bin/gmsh"

    # --m_coarse 10 --m_normal 8 --m_gap 0.5 --m_sl_top 4.0 --m_sl_bot 1.0 --m_r_in 10 \
python rotor_geo.py --Qr 30 --N_rs 30 \
    --R_rin 8.5 --R_rout 35.25 --R_g 35.41 --b_1 0.2 --h_1 0.1 --b_4 3.4 --b_5 2.0 --h_5 10.0 \
    --template templates/im_rotor_modified.geo

python stator_geo.py --template templates/im_stator_double_layer.geo --Qs 24 --N_ss 24 \
    --m_coarse 20 --m_normal 12 --m_gap 0.55 --m_sl_top 7 --m_sl_bot 1.5 --m_s_out 12 \
    --R_sin 35.6 --R_sout 60 --R_g 35.41 --b_5 7.75 --b_1 3.0 --h_1 0.8 --h_2 0.8 \
    --b_4 5 --h_5 12
# python stator_geo.py --template ../gmsh/im_stator.geo --Qs 48 --N_ss 48

$gmsh im_stator.geo -2 -o im_stator.msh
ElmerGrid 14 2 im_stator.msh -2d -autoclean -names

$gmsh im_rotor.geo -2 -o im_rotor.msh
ElmerGrid 14 2 im_rotor.msh -2d -autoclean -names

ElmerGrid 2 2 im_stator -in im_rotor -unite -autoclean -names -out im
rm -rf im_stator im_rotor im_stator.msh im_rotor.msh

# parallel partitioning
np=4     #number of partitions and parallel processes
# ElmerGrid 2 2 im -partdual -partlayers 0 -metis $np 3 -connect 2 3 4 5 7 8
ElmerGrid 2 2 im -partdual -metis $np 4 -connect 2 3 4 5 7 8   # without partlayers 0 there is a discrepancy between NF torque and band torque

# generate rotor cage winding equations and components
# parameters are in the begining of the cage_generator.py script
cd cage
python cage_generator.py
cd ..

# python model_sif.py
# ElmerSolver model.sif

python transient_sif.py
# ElmerSolver transient.sif
# parallel execution
echo "transient.sif" > ELMERSOLVER_STARTINFO
mpirun -np $np ElmerSolver_mpi 