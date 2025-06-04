// skb_utils/src/logging.rs
use crate::error::UtilsError; // Use UtilsError from the same crate
use env_logger::Builder;
use log::LevelFilter;
use std::io::Write; // Required for Builder::format

pub fn setup_logging(default_level: Option<&str>) -> Result<(), UtilsError> {
    let level = match default_level {
        Some(lvl_str) => match lvl_str.to_lowercase().as_str() {
            "error" => LevelFilter::Error,
            "warn" => LevelFilter::Warn,
            "info" => LevelFilter::Info,
            "debug" => LevelFilter::Debug,
            "trace" => LevelFilter::Trace,
            _ => LevelFilter::Info, // Default to Info if string is unrecognized
        },
        None => LevelFilter::Info, // Default to Info if no level is provided
    };

    Builder::new()
        .filter_level(level) // Set the default filter level programmatically
        .format(|buf, record| {
            writeln!(
                buf,
                "{} [{}] - {}",
                chrono::Local::now().format("%Y-%m-%dT%H:%M:%S%.3f"), // Timestamp
                record.level(),                                       // Log level
                record.args()                                         // Message
            )
        })
        .try_init() // Returns Result<(), log::SetLoggerError>
        .map_err(UtilsError::LoggerError) // Map to UtilsError::LoggerError
}
