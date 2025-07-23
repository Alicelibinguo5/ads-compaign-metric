#!/bin/bash

# Mermaid Diagram Renderer
# This script helps render Mermaid diagrams from markdown files

set -e

echo "🎨 Mermaid Diagram Renderer"
echo "=========================="

# Check if mmdc is installed
if ! command -v mmdc &> /dev/null; then
    echo "❌ Mermaid CLI not found. Installing..."
    npm install -g @mermaid-js/mermaid-cli
fi

# Create output directory
mkdir -p mermaid_output

echo "📊 Rendering diagrams from docs/architecture_diagram.md..."

# Extract and render the first diagram (graph TB)
cat > temp_diagram1.mmd << 'EOF'
graph TB
    %% Color definitions
    classDef source fill:#FF6B6B,stroke:#FF5252,stroke-width:2px,color:#fff
    classDef kafka fill:#FFD93D,stroke:#FFC107,stroke-width:2px,color:#000
    classDef flink fill:#4ECDC4,stroke:#26A69A,stroke-width:2px,color:#fff
    classDef storage fill:#45B7D1,stroke:#2196F3,stroke-width:2px,color:#fff
    classDef dashboard fill:#9C27B0,stroke:#7B1FA2,stroke-width:2px,color:#fff

    %% Data Sources
    subgraph "📱 Data Sources"
        APP[Mobile & Web Apps]:::source
    end

    %% Kafka Layer
    subgraph "📊 Kafka"
        KAFKA[Kafka Broker]:::kafka
        TOPIC[Campaign Events Topic]:::kafka
    end

    %% Flink Processing
    subgraph "🔄 Flink Processing"
        FLINK[Flink JobManager]:::flink
        PROCESS[Real-time Processing<br/>• Parse Events<br/>• Calculate Metrics<br/>• Aggregate by Campaign]:::flink
    end

    %% Storage
    subgraph "💾 Data Storage"
        ICEBERG[Iceberg Tables<br/>• Campaign Metrics<br/>• User Events]:::storage
    end

    %% Dashboard
    subgraph "📈 Dashboard"
        SUPERSET[Apache Superset]:::dashboard
        DASH[Campaign Dashboard<br/>• CTR, CVR, Revenue<br/>• Real-time Metrics]:::dashboard
    end

    %% Simple Data Flow
    APP -->|Campaign Events| TOPIC
    TOPIC --> KAFKA
    KAFKA -->|Stream Events| FLINK
    FLINK --> PROCESS
    PROCESS -->|Write Metrics| ICEBERG
    ICEBERG -->|Query Data| SUPERSET
    SUPERSET --> DASH
EOF

# Extract and render the second diagram (sequenceDiagram)
cat > temp_diagram2.mmd << 'EOF'
sequenceDiagram
    participant App as Mobile/Web App
    participant Kafka as Kafka
    participant Flink as Flink
    participant Iceberg as Iceberg
    participant Superset as Superset

    App->>Kafka: Campaign Event (impression/click/conversion)
    Kafka->>Flink: Stream Event
    Flink->>Flink: Process & Aggregate
    Flink->>Iceberg: Write Metrics
    Iceberg->>Superset: Query Data
    Superset->>Superset: Display Dashboard
EOF

# Render diagrams
echo "🔄 Rendering architecture diagram..."
mmdc -i temp_diagram1.mmd -o mermaid_output/architecture_diagram.png -b transparent

echo "🔄 Rendering sequence diagram..."
mmdc -i temp_diagram2.mmd -o mermaid_output/sequence_diagram.png -b transparent

# Cleanup
rm temp_diagram1.mmd temp_diagram2.mmd

echo ""
echo "✅ Diagrams rendered successfully!"
echo "📁 Output files:"
echo "  - mermaid_output/architecture_diagram.png"
echo "  - mermaid_output/sequence_diagram.png"
echo ""
echo "🌐 Online Mermaid Editor: https://mermaid.live"
echo "📖 VS Code Extension: bierner.markdown-mermaid" 