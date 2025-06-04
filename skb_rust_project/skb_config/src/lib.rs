// skb_config/src/lib.rs
pub mod error;
pub use error::ConfigError;

pub mod types;
pub use types::Config;
// If you had AdvancedSettings and wanted to re-export it:
// pub use types::AdvancedSettings;

pub mod loader;
pub use loader::load_config;
