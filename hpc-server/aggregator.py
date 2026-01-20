import grpc
from concurrent import futures
import biosignal_pb2
import biosignal_pb2_grpc
import onnxruntime as ort
import numpy as np
import os

class BioNetAggregator(biosignal_pb2_grpc.BioNetServiceServicer):
    def __init__(self):
        # HPC Focus: Load the optimized ONNX model
        model_path = "bio_logic.onnx"
        self.session = ort.InferenceSession(model_path)
        print(f"Loaded ONNX Model from {model_path}")

    def SendSignal(self, request, context):
        # Prepare input for ONNX (numpy array)
        input_data = np.array([[request.value]], dtype=np.float32)
        
        # HPC Focus: Run high-performance inference
        outputs = self.session.run(None, {'input': input_data})
        seizure_prob = outputs[0][0][0]

        is_anomaly = seizure_prob > 0.5
        
        print(f"[INFER] Silo: {request.hospital_id} | Val: {request.value:.2f} | Prob: {seizure_prob:.4f} | Anomaly: {is_anomaly}")

        return biosignal_pb2.SignalResponse(
            status="PROCESSED",
            trigger_training=is_anomaly or request.is_burst
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    biosignal_pb2_grpc.add_BioNetServiceServicer_to_server(BioNetAggregator(), server)
    server.add_insecure_port('[::]:50051')
    print("HPC gRPC Aggregator with ONNX active on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()