// skb_config/src/types.rs
use serde::Deserialize;

#[derive(Debug, Deserialize, Clone)]
pub struct Config {
    // Common application settings
    pub log_level: Option<String>, // e.g., "INFO", "DEBUG"
    pub bot_name: Option<String>,

    // Placeholder for game-related or operational settings
    // These are GUESSES and LIKELY NEED TO BE CHANGED
    pub game_window_title: Option<String>,
    pub scan_interval_ms: Option<u64>,

    // Example of a nested structure, if applicable
    // pub advanced_settings: Option<AdvancedSettings>,
}

// Example of a nested struct, if you have one.
// #[derive(Debug, Deserialize, Clone)]
// pub struct AdvancedSettings {
//     pub feature_flag_x: bool,
//     pub retry_attempts: u32,
// }

// Default implementation - this will also LIKELY NEED ADJUSTMENT
// or be removed if all fields are truly optional and loaded by config-rs
impl Default for Config {
    fn default() -> Self {
        Config {
            log_level: Some("INFO".to_string()),
            bot_name: Some("SKBot".to_string()),
            game_window_title: None,
            scan_interval_ms: Some(1000),
            // advanced_settings: Some(AdvancedSettings::default()),
        }
    }
}

// impl Default for AdvancedSettings {
//     fn default() -> Self {
//         AdvancedSettings {
//             feature_flag_x: false,
//             retry_attempts: 3,
//         }
//     }
// }
