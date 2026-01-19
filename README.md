BioNet-HPC/
├── protos/               # The "Contract": gRPC interface definitions
│   └── biosignal.proto
├── silo-client/          # Simulated Hospital Node (Sensor + gRPC Client)
│   ├── sensor.py         # ECE Signal Logic
│   ├── client.py         # gRPC Networking Logic
│   └── Dockerfile
├── hpc-server/           # Aggregator Node (gRPC Server)
│   ├── aggregator.py     # Aggregation Logic
│   └── Dockerfile
├── k8s/                  # Kubernetes Infrastructure
│   ├── namespaces.yaml
│   ├── network-policies.yaml
│   └── services.yaml
├── ansible/              # Automation
│   └── deploy.yml
├── Makefile              # Unified Command Interface
└── venv/                 # Virtual Environment