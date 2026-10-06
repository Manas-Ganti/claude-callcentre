---
id: isaac-lab-2-1-mobile-robot-bring-up-misc-gotchas-and-verific-9bc4
title: 'Isaac Lab 2.1 mobile-robot bring-up: misc gotchas and verification method'
agent: rtn-playbook-export
project: robotics-rl-payload-transport
domain:
- env
- isaac-sim
- eval
created: '2026-10-06T01:00:29'
filed_as:
- verifying-isaac-lab-physics-silent-failures-dominate-so-prob-57db
- isaac-lab-episodes-leak-state-and-runs-are-nondeterministic-9d53
- attaching-a-payload-body-to-an-isaac-lab-articulation-rigidb-1bad
- payload-x-slope-has-no-effect-on-a-wheeled-robot-in-isaac-la-8c57
- robots-drive-off-floating-ground-patches-or-tip-at-the-edge-09cd
- per-env-slopes-in-isaac-lab-from-tilted-kinematic-cuboids-wr-42a6
- before-training-a-robot-policy-check-the-robot-can-do-the-ta-eae8
closed: '2026-10-06T01:11:12'
---
Source: docs/ISAAC_SIM_PLAYBOOK.md (bring-up 2026-09-24/26, Isaac Sim 4.5.0 pip + Isaac Lab v2.1.0, 1x L40S on VT ARC Falcon). All verified on ARC in earlier sessions unless noted.

1. Silent failures dominate: most Isaac/PhysX bugs produce plausible wrong numbers, no exception. Every study axis needs a forced-condition probe measuring the physical response (friction slip at mu high vs low, slope rest height, forward/turn probe for wheel sign/radius). Read values back from root_physx_view.get_*.
2. Probe hygiene: probes force all envs to one condition -> snapshot spread checks BEFORE probes (forgetting caused 3 false FAILs).
3. Reset joint state too (write_joint_state_to_sim with defaults) or wheel spin/caster angle carry over between episodes.
4. Seed via env_cfg.seed; else 'Seed not set' warning and nondeterminism.
5. Adding a body (payload) to an articulation: author Xform with RigidBodyAPI+MassAPI under /World/envs/env_0/Robot plus UsdPhysics.FixedJoint to chassis BEFORE clone_environments; PhysX composes mass/COM/inertia. Adding mass to chassis_link moved COM toward axle of a robot with no front support (Carter) -> tipping.
6. USD default drive maxForce=inf removes payload x slope effects; set effort_limit_sim (the physics torque cap for implicit actuators; velocity_limit ignored, effort_limit is alias/deprecated). Mark physically infeasible OOD cells and exclude from degradation metrics.
7. Floating ground patches: nothing stops robot driving off; terminate on out-of-bounds. Sample start/goal/A* with an edge band of one robot radius or caster overhangs edge and robot tips (7/64 envs every run).
8. Kinematic RigidObject poses via write_root_pose_to_sim do move (0.000 m error); tilted kinematic cuboid works as per-env slope; R_y(-theta) makes +x uphill.
9. Check the robot can physically do the task before training: JetBot (2 kg, 3 cm wheels) reached 0.38 of a 1.5 m/s command with payload -> replaced by Carter.
10. Eval sanity triad through one harness: random policy (floor), classical baseline (must succeed in-distribution first; Nav2 had ~20% flat collisions before wheel-radius fix), trained policy.
11. Throughput (Carter, 2048 envs, L40S): 28-36k env-steps/s; PPO 3000 it x 24 steps = 147M steps in 74-81 min; collection-bound by CPU terrain gen + A* -> --cpus-per-task=16.
12. Diagnose from evidence before fixing: a guessed fix cost a queue round; cause was visible in collected data. Batch fixes per sbatch round.
