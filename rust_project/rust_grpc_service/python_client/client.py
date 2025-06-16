# Python gRPC client for RankingService
import grpc
import ranking_pb2
import ranking_pb2_grpc


def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = ranking_pb2_grpc.RankingServiceStub(channel)

    # Test Ping
    response = stub.Ping(ranking_pb2.Empty())
    print(f"Ping response: {response.message}")

    # Test GetSampleRanking
    ranking_response = stub.GetSampleRanking(ranking_pb2.Empty())
    print("Sample ranking:")
    for item in ranking_response.items:
        print(f"  value={item.value}, rank={item.rank}")

if __name__ == '__main__':
    run()
