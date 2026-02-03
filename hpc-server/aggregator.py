import grpc
from concurrent import futures
import biosignal_pb2
import biosignal_pb2_grpc
import onnxruntime as ort
import numpy as np
import os
import json
import time
# Azure SDK Imports
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient

# CNE Config: URL from environment variable
ADT_URL = os.getenv("ADT_URL")

class BioNetAggregator(biosignal_pb2_grpc.BioNetServiceServicer):
    def __init__(self):
        # HPC Focus: Load the optimized ONNX model
        model_path = "bio_logic.onnx"
        self.session = ort.InferenceSession(model_path)
        print(f"Loaded ONNX Model from {model_path}")
        
        # Initialize Azure Bridge
        self.adt_client = None
        if ADT_URL:
            try:
                cred = DefaultAzureCredential()
                self.adt_client = DigitalTwinsClient(ADT_URL, cred)
                print(f"✅ Connected to Azure Digital Twin: {ADT_URL}")
            except Exception as e:
                print(f"⚠️ Azure Initialization Failed: {e}")

    def SendSignal(self, request, context):
        # Prepare input for ONNX
        input_data = np.array([[request.value]], dtype=np.float32)
        
        # HPC Focus: High-performance inference
        outputs = self.session.run(None, {'input': input_data})
        seizure_prob = outputs[0][0][0]
        is_anomaly = seizure_prob > 0.5
        
        print(f"[INFER] Silo: {request.hospital_id} | Prob: {seizure_prob:.2f} | Anomaly: {is_anomaly}")

        # --- PHASE 6: WEIGHT CAPTURE FOR FEDERATED LEARNING ---
        if request.is_burst:
            self.save_local_weights(request.hospital_id, seizure_prob)

        # --- PHASE 5: AZURE CLOUD MIRROR ---
        if self.adt_client and (is_anomaly or request.is_burst):
            self.sync_to_azure(request.hospital_id, request.value, is_anomaly)

        return biosignal_pb2.SignalResponse(
            status="PROCESSED",
            trigger_training=is_anomaly or request.is_burst
        )

    def save_local_weights(self, hospital_id, prob):
        # HPC Simulation: Simulate weight extraction from the 1D-CNN
        weight_data = {
            "hospital": hospital_id,
            "seizure_probability": float(prob),
            "timestamp": time.time(),
            # Simulating 5 weight parameters for aggregation
            "weights": [float(x) for x in np.random.rand(5)] 
        }
        # Save to the mounted PVC
        filename = f"/app/weights/update_{hospital_id}_{int(time.time()*1000)}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(weight_data, f)
            print(f"📦 Local weights saved for {hospital_id}")
        except Exception as e:
            print(f"❌ Weight Save Error: {e}")

    def sync_to_azure(self, twin_id, val, critical):
            native_val = float(val)
            native_critical = bool(critical)

            patch = [
                {"op": "add", "path": "/HeartRate", "value": native_val},
                {"op": "add", "path": "/IsCritical", "value": native_critical}
            ]
            try:
                self.adt_client.update_digital_twin(twin_id, patch)
                print(f"☁️  Azure Sync Success: Twin '{twin_id}' updated.")
            except Exception as e:
                print(f"❌ Azure Sync Error ({twin_id}): {e}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    biosignal_pb2_grpc.add_BioNetServiceServicer_to_server(BioNetAggregator(), server)
    server.add_insecure_port('[::]:50051')
    print("HPC Aggregator active (Phase 6 Weight Capture enabled)...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()