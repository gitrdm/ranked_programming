use tonic::{transport::Server, Request, Response, Status};
use ranking::ranking_service_server::{RankingService, RankingServiceServer};
use ranking::{Empty, Pong, SampleRankingResponse, RankedItem};
use tracing::info;

pub mod ranking {
    tonic::include_proto!("ranking");
}

#[derive(Debug, Default)]
pub struct MyRankingService;

#[tonic::async_trait]
impl RankingService for MyRankingService {
    async fn ping(&self, _request: Request<Empty>) -> Result<Response<Pong>, Status> {
        info!("Received Ping request");
        Ok(Response::new(Pong { message: "pong".into() }))
    }

    async fn get_sample_ranking(&self, _request: Request<Empty>) -> Result<Response<SampleRankingResponse>, Status> {
        info!("Received GetSampleRanking request");
        let items = vec![RankedItem { value: "a".into(), rank: 0 }, RankedItem { value: "b".into(), rank: 1 }];
        Ok(Response::new(SampleRankingResponse { items }))
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::fmt::init();
    let addr = "[::1]:50051".parse()?;
    let service = MyRankingService::default();
    info!("Starting gRPC server on {}", addr);
    Server::builder()
        .add_service(RankingServiceServer::new(service))
        .serve(addr)
        .await?;
    Ok(())
}
