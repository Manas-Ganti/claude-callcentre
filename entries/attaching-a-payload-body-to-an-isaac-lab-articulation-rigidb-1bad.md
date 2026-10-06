---
id: attaching-a-payload-body-to-an-isaac-lab-articulation-rigidb-1bad
kind: convention
title: Attaching a payload body to an Isaac Lab articulation (RigidBodyAPI + FixedJoint before clone_environments)
domain:
- isaac-sim
- env
stack:
  isaacsim: 4.5.0 (pip)
  isaaclab: v2.1.0
  gpu: 1x L40S
  cluster: VT ARC Falcon
symptoms:
- How to add a payload / extra mass to a robot articulation in Isaac Lab
- Robot tips after adding mass to chassis_link
root_cause: ''
fix: Author an Xform with RigidBodyAPI + MassAPI under /World/envs/env_0/Robot plus a UsdPhysics.FixedJoint
  to the chassis, BEFORE clone_environments; PhysX composes mass, COM and inertia. Don't just add mass
  to chassis_link.
failed_attempts:
- 'Adding mass to chassis_link: moved the COM toward the axle of a robot with no front support (Carter)
  and it tipped'
verify: ''
status: verified
uses: 1
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: '2026-09-26'
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Attaching a payload body to an Isaac Lab articulation (RigidBodyAPI + FixedJoint before clone_environments)

> [!success] convention · verified · used 1×, failed 0× · last verified 2026-09-26
> #isaac-sim #env #kind/convention #status/verified

## Symptoms
```text
How to add a payload / extra mass to a robot articulation in Isaac Lab
Robot tips after adding mass to chassis_link
```

## Convention
Author an Xform with RigidBodyAPI + MassAPI under /World/envs/env_0/Robot plus a UsdPhysics.FixedJoint to the chassis, BEFORE clone_environments; PhysX composes mass, COM and inertia. Don't just add mass to chassis_link.

## Failed attempts
- Adding mass to chassis_link: moved the COM toward the axle of a robot with no front support (Carter) and it tipped

## Stack
| | |
|---|---|
| isaacsim | 4.5.0 (pip) |
| isaaclab | v2.1.0 |
| gpu | 1x L40S |
| cluster | VT ARC Falcon |

<small>created 2026-10-06 · id `attaching-a-payload-body-to-an-isaac-lab-articulation-rigidb-1bad`</small>

## Notes

<!-- callcentre:end -->
From robotics-rl-payload-transport docs/ISAAC_SIM_PLAYBOOK.md (agent rtn-playbook-export); verified on ARC Falcon L40S during bring-up 2026-09-24/26.
