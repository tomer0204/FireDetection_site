use anyhow::Result;
use async_trait::async_trait;
use ort::execution_providers::{CUDAExecutionProvider, CPUExecutionProvider, ExecutionProvider};
use ort::session::Session;
use ort::value::Tensor as OrtTensor;
use std::path::Path;

use crate::io::{RawOutput, Tensor};

#[async_trait]
pub trait YoloBackend: Send + Sync {
    async fn infer(&mut self, input: &Tensor) -> Result<RawOutput>;
}

pub struct OnnxBackend {
    session: Session,
    input_name: String,
}

impl OnnxBackend {
    pub fn new<P: AsRef<Path>>(path: P) -> Result<Self> {
        let cuda = CUDAExecutionProvider::default();
        let has_cuda = cuda.is_available()?;

        let builder = if has_cuda {
            Session::builder()?.with_execution_providers([cuda.build()])?
        } else {
            Session::builder()?.with_execution_providers([CPUExecutionProvider::default().build()])?
        };

        let session = builder.commit_from_file(path)?;
        let input_name = session.inputs()[0].name().to_string();

        Ok(Self { session, input_name })
    }
}

#[async_trait]
impl YoloBackend for OnnxBackend {
    async fn infer(&mut self, input: &Tensor) -> Result<RawOutput> {
        let dims = [input.shape[0], input.shape[1], input.shape[2], input.shape[3]];
        let input_tensor = OrtTensor::from_array((dims, input.data.clone()))?;

        let outputs = self
            .session
            .run(ort::inputs![self.input_name.as_str() => input_tensor])?;

        let (shape, data) = outputs[0].try_extract_tensor::<f32>()?;

        let shape = shape.iter().map(|d| *d as usize).collect();
        let data = data.iter().cloned().collect();

        Ok(RawOutput { shape, data })
    }
}