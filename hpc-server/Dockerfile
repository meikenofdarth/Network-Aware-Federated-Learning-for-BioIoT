FROM python:3.9-slim
WORKDIR /app
# HPC Requirement: Install onnxruntime
RUN pip install grpcio grpcio-tools onnxruntime numpy
COPY hpc-server/aggregator.py .
COPY bio_logic.onnx . 
COPY biosignal_pb2.py .
COPY biosignal_pb2_grpc.py .
ENV PYTHONUNBUFFERED=1
EXPOSE 50051
CMD ["python", "aggregator.py"]