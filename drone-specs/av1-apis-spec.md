# Aerovora Bee Drone — Model AV-1 Specification

## Overview

The AV-1 "Apis" is a fully autonomous hexacopter designed for precision plant caretaking. It replaces chemical spraying, manual pollination, and visual inspection with AI-driven micro-interventions at the single-plant level.

---

### Airframe

| Property | Value |
|----------|-------|
| Rotors | 6 (coaxial contra-rotating pairs) |
| Diameter | 1.2m (39 in) |
| Dry Weight | 3.8 kg (8.4 lbs) |
| MTOW | 6.2 kg (13.7 lbs) |
| Frame Material | Carbon fiber + aerospace aluminum |
| IP Rating | IP54 (dust + splash resistant) |

---

### Propulsion

| Property | Value |
|----------|-------|
| Motors | 6x brushless DC, 420KV |
| Propellers | 12x4.5" carbon fiber, folding |
| Max Speed | 15 m/s (33 mph) |
| Cruise Speed | 6 m/s (13 mph) |
| Max Climb | 5 m/s |
| Max Wind Resistance | 12 m/s (27 mph) |

---

### Power

| Property | Value |
|----------|-------|
| Battery | 6S 22,000mAh Li-Ion (swappable) |
| Flight Time | 35 min (hover), 28 min (cruise) |
| Charge Time | 45 min (fast charge station) |
| Hot-swap | Automated battery swapping station |
| Solar Charging | Optional ground station array |

---

### Payload Modules (Interchangeable)

| Module | Function | Weight |
|--------|----------|--------|
| Pollination Wand | Electrostatic pollen applicator, 500g reservoir | 620g |
| Micro-Sprayer | Precision nozzle array, 2L tank, droplet sizes 50-400μm | 850g |
| Hyperspectral Camera | 5-band (RGB, NIR, Red-edge, thermal) | 340g |
| LIDAR Scanner | 360° solid-state, 100m range, 2cm accuracy | 280g |
| Sampler | Contact-based leaf/soil sample collector | 410g |

---

### Computing & AI

| Property | Value |
|----------|-------|
| Flight Controller | Pixhawk 6X + ARM Cortex-M7 |
| Vision Computer | NVIDIA Jetson Orin NX 16GB |
| AI Accelerator | 2x Intel Movidius VPUs |
| Cameras | 4x stereo (forward, downward, omnidirectional) |
| Connectivity | 5G, WiFi 6, LoRa mesh (swarm comms) |
| RTK GPS | ±2.5cm accuracy |
| Obstacle Avoidance | 360° IR + ultrasonic, 20m range |

---

### Plant Care Capabilities

| Capability | Detail |
|------------|--------|
| Pollination | Per-flower electrostatic pollen transfer, 95%+ success rate |
| Disease Detection | CNN-based leaf analysis, 98.2% accuracy across 47 crop types |
| Nutrient Deficiency | Spectral analysis, 22 detectable deficiency patterns |
| Pest Detection | Visual + thermal, 31 pest species identified |
| Micro-Spraying | 2cm precision, 92% reduction in chemical use vs broadcast |
| Yield Forecasting | Per-plant bud/fruit count, ±5% accuracy at 30 days out |
