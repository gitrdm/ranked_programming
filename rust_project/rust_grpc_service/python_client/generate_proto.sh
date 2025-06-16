# Generate Python gRPC code from ranking.proto
python -m grpc_tools.protoc \
    --proto_path=../proto \
    --python_out=. \
    --grpc_python_out=. \
    ../proto/ranking.proto
