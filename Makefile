.PHONY: build deploy run-hospitals clean

# Use the python interpreter from the venv
PYTHON := python3

build:
	eval $$(minikube docker-env) && \
	$(PYTHON) hpc-server/generate_model.py && \
	docker build -t hpc-aggregator:v1 -f hpc-server/Dockerfile . && \
	docker build -t silo-client:v1 -f silo-client/Dockerfile .

deploy:
	kubectl label ns hospital-a kubernetes.io/metadata.name=hospital-a --overwrite || true
	kubectl label ns hospital-b kubernetes.io/metadata.name=hospital-b --overwrite || true
	kubectl label ns aggregator kubernetes.io/metadata.name=aggregator --overwrite || true
	kubectl apply -f k8s/infra.yaml
	kubectl apply -f k8s/hpc-scaler.yaml

run-hospitals:
	# Hospital A (Silo Alpha)
	kubectl delete pod test-client -n hospital-a --ignore-not-found
	kubectl run test-client -n hospital-a --image=silo-client:v1 \
		--env="AGGREGATOR_ADDR=aggregator-service.aggregator.svc.cluster.local:50051" \
		--env="HOSPITAL_ID=Silo-Alpha"
	
	# Hospital B (Silo Beta) - To prove Multi-tenancy
	kubectl delete pod test-client -n hospital-b --ignore-not-found
	kubectl run test-client -n hospital-b --image=silo-client:v1 \
		--env="AGGREGATOR_ADDR=aggregator-service.aggregator.svc.cluster.local:50051" \
		--env="HOSPITAL_ID=Silo-Beta"

clean:
	kubectl delete pod test-client -n hospital-a --ignore-not-found
	kubectl delete pod test-client -n hospital-b --ignore-not-found