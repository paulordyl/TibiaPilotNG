// Make the settings module and its contents public
pub mod settings;

// Re-export Config and load_config for easier access if desired
pub use settings::{Config, load_config};
