use anyhow::Result;

use crate::io::{Detection, Detections, OutputMeta, RawOutput};

pub fn run(
    raw: &RawOutput,
    conf_th: f32,
    nms_iou: f32,
    max_det: usize,
    input_w: u32,
    input_h: u32,
    model_w: u32,
    model_h: u32,
) -> Result<Detections> {

    let mut dets = match raw.shape.as_slice() {
        // Nx6 format
        [n, 6] => decode_nx6(raw, *n, conf_th)?,

        // format [1,5,N]
        [1, 5, n] => decode_yolo_1x5xn(raw, *n, conf_th)?,

        _ => anyhow::bail!("Unsupported output shape {:?}", raw.shape),
    };

    dets = nms(dets, nms_iou, max_det);

    Ok(Detections {
        detections: dets,
        meta: OutputMeta {
            input_width: input_w,
            input_height: input_h,
            model_width: model_w,
            model_height: model_h,
        },
    })
}

fn decode_nx6(raw: &RawOutput, n: usize, conf: f32) -> Result<Vec<Detection>> {
    if raw.data.len() != n * 6 {
        anyhow::bail!("output data length mismatch");
    }

    let mut out = Vec::new();

    for i in 0..n {
        let base = i * 6;

        let score = raw.data[base + 4];
        if score < conf {
            continue;
        }

        out.push(Detection {
            x1: raw.data[base],
            y1: raw.data[base + 1],
            x2: raw.data[base + 2],
            y2: raw.data[base + 3],
            score,
            class_id: raw.data[base + 5] as i32,
        });
    }

    Ok(out)
}

fn decode_yolo_1x5xn(raw: &RawOutput, n: usize, conf: f32) -> Result<Vec<Detection>> {

    if raw.data.len() != 5 * n {
        anyhow::bail!("unexpected data length for YOLO output");
    }

    let mut out = Vec::new();

    for i in 0..n {

        let cx = raw.data[i];
        let cy = raw.data[n + i];
        let w  = raw.data[2*n + i];
        let h  = raw.data[3*n + i];
        let score = raw.data[4*n + i];

        if score < conf {
            continue;
        }

        let x1 = cx - w / 2.0;
        let y1 = cy - h / 2.0;
        let x2 = cx + w / 2.0;
        let y2 = cy + h / 2.0;

        out.push(Detection {
            x1,
            y1,
            x2,
            y2,
            score,
            class_id: 0,
        });
    }

    Ok(out)
}

fn iou(a: &Detection, b: &Detection) -> f32 {
    let x_left = a.x1.max(b.x1);
    let y_top = a.y1.max(b.y1);
    let x_right = a.x2.min(b.x2);
    let y_bottom = a.y2.min(b.y2);

    let inter_w = (x_right - x_left).max(0.0);
    let inter_h = (y_bottom - y_top).max(0.0);
    let inter = inter_w * inter_h;

    let area_a = (a.x2 - a.x1).max(0.0) * (a.y2 - a.y1).max(0.0);
    let area_b = (b.x2 - b.x1).max(0.0) * (b.y2 - b.y1).max(0.0);

    let union = area_a + area_b - inter;

    if union <= 0.0 {
        0.0
    } else {
        inter / union
    }
}

fn nms(mut dets: Vec<Detection>, iou_th: f32, max_det: usize) -> Vec<Detection> {

    dets.sort_by(|a, b| b.score.partial_cmp(&a.score).unwrap());

    let mut keep: Vec<Detection> = Vec::new();

    for d in dets.into_iter() {

        let mut suppressed = false;

        for k in keep.iter() {
            if iou(&d, k) >= iou_th {
                suppressed = true;
                break;
            }
        }

        if !suppressed {
            keep.push(d);

            if keep.len() >= max_det {
                break;
            }
        }
    }

    keep
}
