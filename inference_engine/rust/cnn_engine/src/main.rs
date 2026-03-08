use axum::{
    body::Bytes,
    extract::State,
    http::StatusCode,
    response::IntoResponse,
    routing::post,
    Json, Router,
};
use image::GenericImageView;
use std::{net::SocketAddr, sync::Arc};
use tokio::sync::Mutex;

use cnn_engine::{
    io::Frame,
    postprocess,
    preprocess,
    process::backend::{OnnxBackend, YoloBackend},
};

struct AppState {
    backend: Mutex<OnnxBackend>,
}

async fn infer_handler(State(state): State<Arc<AppState>>, bytes: Bytes) -> impl IntoResponse {
    let img = match image::load_from_memory(&bytes) {
        Ok(v) => v,
        Err(e) => return (StatusCode::BAD_REQUEST, format!("{e}")).into_response(),
    };

    let (w, h) = img.dimensions();

    let frame = Frame {
        image: img,
        width: w,
        height: h,
    };

    let input = match preprocess::run(&frame, 640, 640) {
        Ok(v) => v,
        Err(e) => return (StatusCode::INTERNAL_SERVER_ERROR, format!("{e}")).into_response(),
    };

    let raw = {
        let mut backend = state.backend.lock().await;
        match backend.infer(&input).await {
            Ok(v) => v,
            Err(e) => return (StatusCode::INTERNAL_SERVER_ERROR, format!("{e}")).into_response(),
        }
    };

    let detections = match postprocess::run(&raw, 0.25, 0.45, 100, w, h, 640, 640) {
        Ok(v) => v,
        Err(e) => return (StatusCode::INTERNAL_SERVER_ERROR, format!("{e}")).into_response(),
    };

    (StatusCode::OK, Json(detections)).into_response()
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let onnx_path = std::env::var("ONNX_PATH").unwrap_or_else(|_| "/models/best.onnx".to_string());

    println!("Loading model from {}", onnx_path);

    let backend = OnnxBackend::new(&onnx_path)?;

    println!("Model loaded");

    let state = Arc::new(AppState {
        backend: Mutex::new(backend),
    });

    let app = Router::new().route("/infer", post(infer_handler)).with_state(state);

    let addr = SocketAddr::from(([0, 0, 0, 0], 8088));
    println!("Server running on {}", addr);

    axum::serve(tokio::net::TcpListener::bind(addr).await?, app).await?;
    Ok(())
}