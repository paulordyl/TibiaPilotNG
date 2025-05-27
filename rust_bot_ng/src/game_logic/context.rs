use std::sync::{Arc, Mutex};
use log::debug; // For logging initialization

#[derive(Debug, Clone)] // Clone might be useful, Debug for logging
pub struct PlayerStats {
    pub hp: u32,
    pub mp: u32,
    pub max_hp: u32,
    pub max_mp: u32,
    // TODO: Add more fields like level, experience as needed
}

impl PlayerStats {
    pub fn new(hp: u32, mp: u32, max_hp: u32, max_mp: u32) -> Self {
        debug!("Creating new PlayerStats: hp={}, mp={}, max_hp={}, max_mp={}", hp, mp, max_hp, max_mp);
        PlayerStats { hp, mp, max_hp, max_mp }
    }

    // Default constructor
    pub fn default() -> Self {
        debug!("Creating default PlayerStats.");
        PlayerStats { hp: 100, mp: 50, max_hp: 100, max_mp: 50 }
    }
}

use crate::config; // For config::settings::HotkeyConfig

#[derive(Debug, Clone)]
pub struct BotSettings {
    pub auto_heal_hp_threshold: u32,
    pub auto_heal_mp_threshold: u32,
    pub heal_hotkey: String, // Added from config
    // TODO: Add other settings as needed, e.g., attack_spell_hotkey
}

impl BotSettings {
    // Updated constructor to include heal_hotkey
    pub fn new(auto_heal_hp_threshold: u32, auto_heal_mp_threshold: u32, heal_hotkey: String) -> Self {
        debug!(
            "Creating new BotSettings: auto_heal_hp_threshold={}, auto_heal_mp_threshold={}, heal_hotkey='{}'",
            auto_heal_hp_threshold, auto_heal_mp_threshold, heal_hotkey
        );
        BotSettings {
            auto_heal_hp_threshold,
            auto_heal_mp_threshold,
            heal_hotkey,
        }
    }

    // Default constructor
    pub fn default() -> Self {
        debug!("Creating default BotSettings.");
        BotSettings {
            auto_heal_hp_threshold: 70,
            auto_heal_mp_threshold: 50,
            heal_hotkey: "f1".to_string(), // Default hotkey if not loaded from config
        }
    }
}

#[derive(Debug)] // GameContext might not need to be Cloneable itself, as its fields are Arc-wrapped
pub struct GameContext {
    pub player_stats: Arc<Mutex<PlayerStats>>,
    pub bot_settings: Arc<Mutex<BotSettings>>,
    pub is_running: Arc<Mutex<bool>>, // Controls main bot loop
}

impl GameContext {
    /// Creates a new GameContext with default player stats and bot settings.
    pub fn new() -> Self {
        debug!("Creating new GameContext with default PlayerStats and BotSettings.");
        GameContext {
            player_stats: Arc::new(Mutex::new(PlayerStats::default())),
            bot_settings: Arc::new(Mutex::new(BotSettings::default())),
            is_running: Arc::new(Mutex::new(true)), // Bot starts in a running state
        }
    }

    /// Creates a new GameContext with provided initial values.
    #[allow(dead_code)] // Keep this for flexibility, even if not immediately used.
    // Method to update settings from loaded config, useful if GameContext is created before config is loaded
    // Or, GameContext::new can take initial BotSettings.
    pub fn update_from_config(&mut self, config_hotkeys: &config::settings::HotkeyConfig) {
        self.heal_hotkey = config_hotkeys.heal.clone();
        // self.attack_spell_hotkey = config_hotkeys.attack_spell.clone(); // Example
        debug!("BotSettings updated from config: heal_hotkey='{}'", self.heal_hotkey);
    }
}


// GameContext's new() method might need adjustment if BotSettings::default() changes significantly
// or if BotSettings should be initialized from loaded Config before GameContext is created.
// For now, GameContext::new() uses BotSettings::default().
// It's often better to load config, then create GameContext with parts of that config.

#[derive(Debug)] // GameContext might not need to be Cloneable itself, as its fields are Arc-wrapped
pub struct GameContext {
    pub player_stats: Arc<Mutex<PlayerStats>>,
    pub bot_settings: Arc<Mutex<BotSettings>>, // This will hold BotSettings initialized from Config
    pub is_running: Arc<Mutex<bool>>, // Controls main bot loop
}

impl GameContext {
    /// Creates a new GameContext with default player stats and bot settings.
    /// For BotSettings to be properly initialized from config, it should be passed in.
    pub fn new(initial_bot_settings: BotSettings) -> Self {
        debug!("Creating new GameContext with provided BotSettings.");
        GameContext {
            player_stats: Arc::new(Mutex::new(PlayerStats::default())),
            bot_settings: Arc::new(Mutex::new(initial_bot_settings)),
            is_running: Arc::new(Mutex::new(true)), // Bot starts in a running state
        }
    }

    /// Creates a new GameContext with provided initial values, including full BotSettings.
    #[allow(dead_code)] // Keep this for flexibility, even if not immediately used.
    pub fn with_initial_values(initial_stats: PlayerStats, initial_settings: BotSettings, initial_is_running: bool) -> Self {
        debug!("Creating new GameContext with provided initial values.");
        GameContext {
            player_stats: Arc::new(Mutex::new(initial_stats)),
            bot_settings: Arc::new(Mutex::new(initial_settings)),
            is_running: Arc::new(Mutex::new(initial_is_running)),
        }
    }

    // Example methods to interact with the context (optional, can also be done directly)

    pub fn get_player_hp(&self) -> u32 {
        self.player_stats.lock().unwrap().hp
    }

    pub fn set_is_running(&self, running: bool) {
        let mut is_running_lock = self.is_running.lock().unwrap();
        *is_running_lock = running;
        debug!("GameContext is_running set to: {}", running);
    }

    pub fn check_is_running(&self) -> bool {
        *self.is_running.lock().unwrap()
    }
}

// Default implementation for GameContext calls new() with default BotSettings
impl Default for GameContext {
    fn default() -> Self {
        Self::new(BotSettings::default())
    }
}
