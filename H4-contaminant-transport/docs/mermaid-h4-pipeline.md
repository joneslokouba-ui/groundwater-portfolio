# H4 Pipeline — Contaminant Transport Simulator

```mermaid
flowchart TD
    A[H3 velocity field: q vectors on grid] --> B[Seed particles at source term]
    B --> C[Per-timestep update loop]
    C --> D[Advection: displace along local q]
    C --> E[Dispersion: random-walk step, scaled to dispersivity]
    C --> F[Retardation: velocity multiplier 1/R]
    C --> G[Decay: per-step survival probability]
    D --> H[Updated particle positions]
    E --> H
    F --> H
    G --> H
    H --> I{More timesteps?}
    I -- yes --> C
    I -- no --> J[Full particle trajectory history]
    J --> K[Streamlit Dashboard: animated plume, time slider,
              flow-net overlay from H3, live parameter sliders]

    L[H2: biostimulation / bioaugmentation notes] -.optional decay-rate presets.-> G
```

**Known limitation (see ADR-001):** particle tracking trades exact mass-balance
accounting for visual/interactive clarity. A grid-based mass-balance check is
deferred to v2.
