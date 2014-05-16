FFXIV-DPS-Simulation
========================

#####To Do
- [ ] Split classes in separate files for functionalities
  - [ ] Statistics
  - [ ] Class/Job Specific rotation module
  - [ ] Damage function module
  - [ ] Tools and main module
- Streamline package usage (to v3.3)
- Write function or class to calculate weights automatically
- Write function to convert attributes to a single dps index (basically normalize using weights and add)
- Write module to store/retrieve gear sets and convert to attributes
- Be able to pass a damage function as a parameter (so that we can easily switch from one model to another)
- Be able to pass a rotation function as a parameter (so that we can keep a family of rotations per job and switch from one to another)
- Generalize to all DoW jobs
- Generalize to multi-targets (so that we can write rotation function for multi-target)
- Write a set of tools to analyze parses
  - crit frequency
  - damage range (per skills or after re-normalization for all skills)
  - damage as f(attributes)
