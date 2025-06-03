use serde::Deserialize;
use std::path::Path;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ConfigError {
    #[error("Configuration loading failed: {0}")]
    LoadError(#[from] config::ConfigError),
    #[error("I/O error related to configuration: {0}")]
    IoError(#[from] std::io::Error),
}

#[derive(Debug, Deserialize, Clone)]
pub struct GeneralSettings {
    pub bot_name: String,
    pub log_level: String,
}

#[derive(Debug, Deserialize, Clone)]
pub struct FeatureXSettings {
    pub enabled: bool,
    pub threshold: i32,
}

#[derive(Debug, Deserialize, Clone)]
pub struct Config {
    pub general: GeneralSettings,
    pub feature_x: FeatureXSettings,
}

fn _assert_config_send_sync() {
    fn assert_send_sync_generic<T: Send + Sync>() {}
    assert_send_sync_generic::<Config>();
}

pub fn load_config(config_path: &Path) -> Result<Config, ConfigError> {
    log::info!("Loading configuration from: {:?}", config_path);
    let builder = config::Config::builder()
        .add_source(config::File::from(config_path))
        .add_source(config::Environment::with_prefix("SKB").separator("__"));

    match builder.build() {
        Ok(cfg) => {
            match cfg.try_deserialize() {
                Ok(deserialized_cfg) => {
                    log::info!("Configuration loaded and deserialized successfully.");
                    Ok(deserialized_cfg)
                }
                Err(e) => {
                    log::error!("Failed to deserialize configuration: {}", e);
                    Err(ConfigError::LoadError(e))
                }
            }
        }
        Err(e) => {
            log::error!("Failed to build configuration: {}", e);
            Err(ConfigError::LoadError(e))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use std::io::Write;
    use std::env;

    fn setup_test_logging() {
        let _ = env_logger::builder().is_test(true).try_init();
    }

    fn create_temp_config_file(dir: &Path, filename: &str, content: &str) -> std::path::PathBuf {
        let file_path = dir.join(filename);
        let mut file = fs::File::create(&file_path).expect("Failed to create temp config file");
        write!(file, "{}", content).expect("Failed to write to temp config file");
        file_path
    }

    #[test]
    fn test_load_valid_ini_config() {
        setup_test_logging();
        let temp_dir = env::temp_dir().join("skb_config_tests_ini");
        fs::create_dir_all(&temp_dir).expect("Failed to create temp dir for config tests");

        let ini_content = "[general]
bot_name = \"TestBotINI\"
log_level = \"INFO\"

[feature_x]
enabled = true
threshold = 123";
        let config_path = create_temp_config_file(&temp_dir, "settings.ini", ini_content);

        let result = load_config(&config_path);
        assert!(result.is_ok(), "Failed to load INI config: {:?}", result.err());

        let config = result.unwrap();
        assert_eq!(config.general.bot_name, "TestBotINI");
        assert_eq!(config.general.log_level, "INFO");
        assert_eq!(config.feature_x.enabled, true);
        assert_eq!(config.feature_x.threshold, 123);

        fs::remove_file(config_path).unwrap();
        fs::remove_dir_all(temp_dir).unwrap();
    }

    #[test]
    fn test_load_valid_json_config() {
        setup_test_logging();
        let temp_dir = env::temp_dir().join("skb_config_tests_json");
        fs::create_dir_all(&temp_dir).expect("Failed to create temp dir for config tests");

        let json_content = r#"{
            "general": { "bot_name": "TestBotJSON", "log_level": "DEBUG" },
            "feature_x": { "enabled": false, "threshold": 456 }
        }"#;
        let config_path = create_temp_config_file(&temp_dir, "settings.json", json_content);

        let result = load_config(&config_path);
        assert!(result.is_ok(), "Failed to load JSON config: {:?}", result.err());

        let config = result.unwrap();
        assert_eq!(config.general.bot_name, "TestBotJSON");
        assert_eq!(config.feature_x.threshold, 456);

        fs::remove_file(config_path).unwrap();
        fs::remove_dir_all(temp_dir).unwrap();
    }

    #[test]
    fn test_load_missing_file() {
        setup_test_logging();
        let temp_dir = env::temp_dir().join("skb_config_tests_missing");
        fs::create_dir_all(&temp_dir).expect("Failed to create temp dir for config tests");
        let non_existent_path = temp_dir.join("non_existent_config_file.ini");

        let result = load_config(&non_existent_path);
        assert!(result.is_err());
        match result.err().unwrap() {
            ConfigError::LoadError(config::ConfigError::Foreign(err_str)) => {
                assert!(err_str.to_lowercase().contains("no such file or directory") || err_str.to_lowercase().contains("could not be found"));
            }
            ConfigError::LoadError(config::ConfigError::FileOpen { .. }) => {}
            e => panic!("Unexpected error type for missing file: {:?}", e),
        }
        fs::remove_dir_all(temp_dir).unwrap();
    }

    #[test]
    fn test_load_invalid_format() {
        setup_test_logging();
        let temp_dir = env::temp_dir().join("skb_config_tests_invalid");
        fs::create_dir_all(&temp_dir).expect("Failed to create temp dir for config tests");

        let invalid_content = "this is not valid ini or json { feature_x = definitely_not_a_bool";
        let config_path = create_temp_config_file(&temp_dir, "invalid_settings.ini", invalid_content);

        let result = load_config(&config_path);
        assert!(result.is_err());
        match result.err().unwrap() {
            ConfigError::LoadError(config::ConfigError::FileParse { .. }) => {}
            e => panic!("Unexpected error type for invalid format: {:?}", e),
        }
        fs::remove_file(config_path).unwrap();
        fs::remove_dir_all(temp_dir).unwrap();
    }

    #[test]
    fn test_load_missing_field() {
        setup_test_logging();
        let temp_dir = env::temp_dir().join("skb_config_tests_missing_field");
        fs::create_dir_all(&temp_dir).expect("Failed to create temp dir for config tests");

        let content = "[general]
bot_name = \"TestBotMissing\"

[feature_x]
enabled = true
threshold = 789";
        let config_path = create_temp_config_file(&temp_dir, "missing_field.ini", content);

        let result = load_config(&config_path);
        assert!(result.is_err());
        match result.err().unwrap() {
            ConfigError::LoadError(config::ConfigError::PathNotFound { key, .. }) => {
                 assert!(key.contains("general.log_level") || key.contains("log_level"));
            }
            ConfigError::LoadError(config::ConfigError::Message(s)) if s.contains("missing field ") => {}
            e => panic!("Unexpected error type for missing field: {:?}", e),
        }
        fs::remove_file(config_path).unwrap();
        fs::remove_dir_all(temp_dir).unwrap();
    }
}
