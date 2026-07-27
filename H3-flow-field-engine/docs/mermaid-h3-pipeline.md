# H3 Pipeline — Flow Field Engine

```mermaid
flowchart TD
    A[Well locations + observed heads (x, y, h)] --> B[Interpolation: IDW / kriging]
    B --> C[Interpolated head grid]
    C --> D[Potentiometric surface: contour heads]
    C --> E[Stream function psi: numerical differentiation]
    E --> F[Streamlines: orthogonal to equipotentials]
    C --> G[Darcy flux: q = -K grad(h)]
    G --> H[Flux vector field]
    D --> I[Streamlit Dashboard]
    F --> I
    H --> I
    I --> J[H4: velocity field input]

    style J fill:#f9f,stroke:#333
```

**Assumption boundary (see ADR-001):** the stream-function derivation (E → F)
is valid only under homogeneous, isotropic K. Heterogeneous-K support is
deferred; UI must label this case as approximate or disable the flow-net
overlay accordingly.