use anyhow::Result;
use image::{imageops::FilterType};

use crate::io::{Frame, Tensor};

pub fn run(frame: &Frame, model_w: u32, model_h: u32) -> Result<Tensor> {
    let resized = frame.image.resize_exact(model_w, model_h, FilterType::Triangle);
    let rgb = resized.to_rgb8();
    let (w, h) = rgb.dimensions();

    let mut out = vec![0.0f32; (3 * w * h) as usize];

    for y in 0..h {
        for x in 0..w {
            let p = rgb.get_pixel(x, y).0;

            let r = (p[0] as f32) / 255.0;
            let g = (p[1] as f32) / 255.0;
            let b = (p[2] as f32) / 255.0;

            let idx = (y * w + x) as usize;
            out[idx] = r;
            out[(w * h) as usize + idx] = g;
            out[(2 * w * h) as usize + idx] = b;
        }
    }

    Ok(Tensor {
        data: out,
        shape: [1, 3, h as usize, w as usize],
    })
}
