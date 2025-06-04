// skb_utils/src/timing.rs
use std::thread;
use std::time::Duration;

/// Pauses the current thread for at least the specified duration in milliseconds.
///
/// Note: The actual duration of sleep may be longer than requested due to
/// OS scheduling, but it will not be shorter.
pub fn precise_delay(duration_ms: u64) {
    thread::sleep(Duration::from_millis(duration_ms));
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::Instant;

    #[test]
    fn test_precise_delay_sleeps_approximately_correct_duration() {
        let delay_ms = 100;
        let tolerance_ms = 50; // Allow some leeway for OS scheduling, etc.

        let start = Instant::now();
        precise_delay(delay_ms);
        let elapsed = start.elapsed().as_millis() as u64;

        // Check if elapsed time is at least the delay and not excessively longer
        // (Precision of sleep is OS-dependent, so this is a basic sanity check)
        assert!(elapsed >= delay_ms, "Delay was shorter than requested: {}ms vs {}ms", elapsed, delay_ms);
        assert!(elapsed <= delay_ms + tolerance_ms, "Delay was much longer than requested: {}ms vs {}ms (tolerance {}ms)", elapsed, delay_ms, tolerance_ms);
    }

    #[test]
    fn test_precise_delay_zero_duration() {
        // Test that a zero duration call completes without panic and quickly
        let start = Instant::now();
        precise_delay(0);
        let elapsed = start.elapsed().as_micros(); // Use micros for zero delay
        assert!(elapsed < 10000, "Zero delay took too long: {}µs", elapsed); // Should be very fast
    }
}
