# 📚 Ads Campaign Metrics - Documentation

## 🎯 **Project Overview**

A simplified, real-time streaming pipeline for tracking advertising campaign performance metrics using Apache Kafka, Flink, and Iceberg.

## 📊 **Core Metrics**

- **CTR (Click-Through Rate)**: Percentage of impressions that result in clicks
- **CVR (Conversion Rate)**: Percentage of clicks that result in conversions  
- **Revenue**: Total revenue generated from ad-driven conversions

## 🏗️ **Architecture**

```
📱 Mobile/Web Apps → 📊 Kafka → 🔄 Flink → 💾 Iceberg → 📈 Superset
```

### **Components**
- **Kafka**: Two topics (campaign_events, dead_letter_queue)
- **Flink**: Real-time processing and aggregation
- **Iceberg**: Two tables (campaign_events, campaign_metrics)
- **Superset**: Single dashboard for visualization

## 📖 **Documentation**

### **Essential Guides**
- **[Architecture Diagram](architecture_diagram.md)**: Visual representation of the system
- **[Implementation Summary](implementation_summary.md)**: Detailed breakdown of the implementation

### **Technical Concepts**
- **[Flink & Iceberg Concepts](flink_iceberg_concepts.md)**: Core concepts and best practices
- **[Superset Dashboard Guide](superset_dashboard_guide.md)**: Dashboard setup and configuration

## 🚀 **Quick Start**

1. **Setup Environment**
   ```bash
   poetry install
   cp env.example .env
   ```

2. **Start Services**
   ```bash
   docker-compose up -d
   ```

3. **Run Pipeline**
   ```bash
   python src/kafka_setup.py
   ```

4. **Setup Dashboard**
   ```bash
   python src/superset/simple_dashboard_setup.py
   ```

5. **View Dashboard**
   - Access Superset at http://localhost:8088
   - Default credentials: admin/admin
   - Follow setup guide in docs/superset_dashboard_guide.md

## 📁 **Project Structure**

```
ads-campaign-metric/
├── src/
│   ├── kafka/          # Kafka producers and consumers
│   ├── flink/          # Flink streaming pipeline
│   ├── superset/       # Superset dashboard setup
│   └── kafka_setup.py
├── config/             # Configuration files
├── docs/               # Documentation
├── tests/              # Test files
├── data/               # Sample data files
└── docker-compose.yml  # Local development setup
```

## 🎯 **Key Benefits**

- **Simplified**: Two topics, basic processing, focused metrics
- **Real-time**: Sub-second latency for campaign insights
- **Scalable**: Easy to extend and modify
- **Production-ready**: Proper error handling and monitoring with DLQ

## 📈 **Performance Targets**

| Component | Throughput | Latency |
|-----------|------------|---------|
| **Kafka** | 10K events/sec | < 50ms |
| **Flink** | 5K events/sec | < 200ms |
| **Iceberg** | 1K writes/sec | < 1s |
| **Superset** | 10 users | < 3s |

---

**Status**: ✅ **READY**  
**Complexity**: 🟢 **MINIMAL**  
**Value**: 🟢 **MAXIMUM** 