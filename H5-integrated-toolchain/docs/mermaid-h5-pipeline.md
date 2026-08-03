# H5 Pipeline Diagram

```mermaid
flowchart TD
    subgraph Thread1["Thread 1 — Predictive / Design"]
        A1[Leapfrog<br/>Geological Model] --> A2[FEFLOW / HydroGeoSphere<br/>Flow & Transport Simulation]
        A2 --> A3[Visual MODFLOW Flex + PEST<br/>Calibration & Uncertainty]
    end

    subgraph Thread2["Thread 2 — Site Characterization / Remediation"]
        B1[Monitoring Well<br/>Network Data] --> B2[Surfer<br/>Concentration Isopleths]
        B2 --> B3[Remediation<br/>Performance Tracking]
    end

    A3 --> C[Python / Streamlit<br/>Connective Layer]
    B3 --> C

    C --> D1[QA/QC Automation]
    C --> D2[PEST Residual<br/>Summary Dashboard]
    C --> D3["Surfer-style" IDW<br/>Contour Reproduction<br/>reuses H3 sim/interpolation.py]

    style Thread1 fill:#eef5ff,stroke:#4a7ab5
    style Thread2 fill:#fff3e6,stroke:#c98a3a
    style C fill:#eafaf1,stroke:#3a9e6b
```

## Notes

- **Thread 1** and **Thread 2** run independently — they represent two different real-world workflow patterns from the candidate's project history (predictive design vs. site characterization), not sequential steps of one project.
- The **Python/Streamlit connective layer** is the only node in this diagram that runs live in the deployed app. Everything upstream of it (Leapfrog, FEFLOW/HydroGeoSphere, Visual MODFLOW Flex/PEST, Surfer) is documented as case-study content, not reproduced.
- `D3` intentionally reuses `H3-flow-field-engine/sim/interpolation.py` rather than reimplementing IDW interpolation, keeping the H5 module consistent with the DRY principle applied across H3/H4.