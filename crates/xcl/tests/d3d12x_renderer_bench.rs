//! Reproducible synthetic benchmarks and regression checks for D3D12.X renderer primitives:
//! frame-clock deadline math, console descriptor heap range allocation, and cross-queue
//! synchronization / bottom-of-pipe CPU writes.

use std::time::Instant;

use xcl::hle::d3d12x::frame;

#[test]
fn bench_frame_clock_deadline_scheduling() {
    const ITERS: u64 = 100_000;
    let base = 1_000_000i64;
    let interval = 166_667i64;
    let offset = 41_667i64;
    let mut acc = 0i64;
    let t0 = Instant::now();
    for i in 0..ITERS {
        let after = base + (i as i64) * 1000;
        let d = frame::next_deadline(base, interval, offset, after);
        acc = acc.wrapping_add(d);
    }
    let elapsed_us = t0.elapsed().as_micros();
    std::hint::black_box(acc);
    assert!(acc != 0);
    eprintln!("bench_frame_clock_deadline_scheduling: {ITERS} iters in {elapsed_us} us");
}

#[test]
fn bench_frame_interval_override_resolution() {
    const ITERS: u64 = 100_000;
    let inputs = [0u32, 8333, 16667, 33333, 50000, 66667];
    let overrides = [None, Some(0), Some(8333), Some(16667)];
    let mut acc = 0u64;
    let t0 = Instant::now();
    for i in 0..ITERS {
        let req = inputs[(i as usize) % inputs.len()];
        let ov = overrides[((i >> 3) as usize) % overrides.len()];
        if let Some(eff) = frame::effective_clock_interval_us(req, ov) {
            acc = acc.wrapping_add(u64::from(eff));
        }
    }
    let elapsed_us = t0.elapsed().as_micros();
    std::hint::black_box(acc);
    assert!(acc > 0);
    eprintln!("bench_frame_interval_override_resolution: {ITERS} iters in {elapsed_us} us");
}
