# 1. Start Minikube
minikube start --cpus 2 --memory 4096 --driver=docker

# 2. Point terminal to Minikube's Docker (CRITICAL: Do this in every new window)
eval $(minikube docker-env)

# 3. Refresh the Metrics Server (Fixes the 'scaling is stuck' bug)
minikube addons disable metrics-server
minikube addons enable metrics-server


# 4. Enter your project folder and activate venv
cd Practical
source venv/bin/activate

# 5. Log in to Azure (Ensures the Bridge can authenticate)
az login

# 6. Apply Namespaces, Network Policies, and the Aggregator
make deploy

# 7. Start the Data Generators (Alpha and Beta)
make run-hospitals


# 8. Check if KEDA is ready to scale
kubectl get scaledobject -n aggregator

# 9. Watch the Aggregator logs to see Azure Syncs
kubectl logs -n aggregator -l app=hpc-aggregator -f --max-log-requests=10