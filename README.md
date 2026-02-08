graph TD
    %% Nodes
    Data[Market Data Feed] --> Governor{RAI Governor<br/>(Gatekeeper)}
    
    %% Tier 3 Logic
    subgraph Tier3 [Tier 3: The General Assembly]
        GenSwarm[Generalist Swarm]
        GenOutput[General Signal]
    end
    
    %% Tier 2 Logic
    subgraph Tier2 [Tier 2: Sector Specialists]
        SecSwarm[Sector Swarms<br/>(Tech, Energy, etc.)]
        SecOutput[Sector Signal]
    end
    
    %% Tier 1 Logic
    subgraph Tier1 [Tier 1: Alpha Hunters]
        AlphaSwarm[Niche 'Clique' Swarms<br/>(High Compute)]
        AlphaOutput[High-Precision Signal]
    end

    %% Flow
    Governor -->|Default State| GenSwarm
    GenSwarm --> GenOutput
    
    %% Triggers
    GenOutput -->|Accuracy < 60% OR Volatility > 1.5| Trigger2{Activate<br/>Specialists?}
    Trigger2 -->|Yes| SecSwarm
    Trigger2 -->|No| FinalResult((Final Output))
    
    SecSwarm --> SecOutput
    SecOutput -->|Complex Alpha Required?| Trigger1{Activate<br/>Alpha Hunters?}
    Trigger1 -->|Yes| AlphaSwarm
    Trigger1 -->|No| FinalResult
    
    AlphaSwarm --> AlphaOutput
    AlphaOutput --> FinalResult
    
    %% Feedback Loop (Sunset Clause)
    AlphaOutput -.->|Performance Check<br/>(Beat GenSwarm by >5%)| KillSwitch{Keep Alive?}
    KillSwitch -.->|No| Governor
    KillSwitch -.->|Yes| AlphaSwarm

    %% Styling
    style Governor fill:#f9f,stroke:#333,stroke-width:2px
    style Tier1 fill:#ffe6e6,stroke:#f00,stroke-width:2px,stroke-dasharray: 5 5
    style Tier3 fill:#e6ffe6,stroke:#0f0,stroke-width:2px
    style FinalResult fill:#fff,stroke:#333,stroke-width:4px
