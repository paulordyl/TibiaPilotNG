use crate::{
    game_logic::{cavebot::core::AllDependencies, context::GameContext}, // For GameContext and AllDependencies
    AppError,
};
use log::{debug, info, error}; // Added error
use std::{sync::Arc, thread, time::Duration};

use crate::{
    game_logic::{cavebot::core::AllDependencies, context::GameContext},
    image_processing, // For digit_recognition
    screen_capture,   // For capture_screen_region
    AppError,
};
use log::{debug, info, error, warn}; // Added warn
use std::{sync::Arc, thread, time::Duration};

// Add a new error variant to AppError for recognition failures if it's not already there.
// This would typically be in your main error enum definition (e.g., in main.rs or a dedicated errors.rs)
// For this example, let's assume AppError has a variant like:
// RecognitionFailed(String),

pub struct PlayerMonitor {
    game_context: Arc<GameContext>,
}

impl PlayerMonitor {
    pub fn new(game_context: Arc<GameContext>) -> Self {
        debug!("Initializing new PlayerMonitor instance.");
        PlayerMonitor { game_context }
    }

    /// Reads HP from the screen using configured region and digit recognition.
    pub fn read_hp_from_screen(&self, deps: &AllDependencies) -> Result<u32, AppError> {
        info!("Attempting to read HP from screen.");
        let hp_region_config = &deps.config.player_status_regions.hp;
        debug!(
            "HP region from config: x={}, y={}, w={}, h={}",
            hp_region_config.x, hp_region_config.y, hp_region_config.width, hp_region_config.height
        );

        let captured_image = screen_capture::capture::capture_screen_region(
            hp_region_config.x,
            hp_region_config.y,
            hp_region_config.width,
            hp_region_config.height,
        )
        .map_err(|e| {
            error!("Failed to capture HP screen region: {}", e);
            e
        })?;
        info!("HP region captured successfully.");

        match image_processing::digit_recognition::recognize_digits_in_region(
            &captured_image,
            &deps.template_manager,
            "digit_", // Assuming "digit_" is the prefix for your digit templates
        ) {
            Ok(Some(hp_value)) => {
                info!("HP recognized from screen: {}", hp_value);
                Ok(hp_value)
            }
            Ok(None) => {
                warn!("HP not recognized from screen region.");
                Err(AppError::ImageProcessingError("HP not recognized".to_string())) // Using existing variant, or add RecognitionFailed
            }
            Err(e) => {
                error!("Error during HP digit recognition: {}", e);
                Err(e)
            }
        }
    }

    /// Reads MP from the screen using configured region and digit recognition.
    pub fn read_mp_from_screen(&self, deps: &AllDependencies) -> Result<u32, AppError> {
        info!("Attempting to read MP from screen.");
        let mp_region_config = &deps.config.player_status_regions.mp;
        debug!(
            "MP region from config: x={}, y={}, w={}, h={}",
            mp_region_config.x, mp_region_config.y, mp_region_config.width, mp_region_config.height
        );

        let captured_image = screen_capture::capture::capture_screen_region(
            mp_region_config.x,
            mp_region_config.y,
            mp_region_config.width,
            mp_region_config.height,
        )
        .map_err(|e| {
            error!("Failed to capture MP screen region: {}", e);
            e
        })?;
        info!("MP region captured successfully.");

        match image_processing::digit_recognition::recognize_digits_in_region(
            &captured_image,
            &deps.template_manager,
            "digit_", // Assuming "digit_" is the prefix for your digit templates
        ) {
            Ok(Some(mp_value)) => {
                info!("MP recognized from screen: {}", mp_value);
                Ok(mp_value)
            }
            Ok(None) => {
                warn!("MP not recognized from screen region.");
                Err(AppError::ImageProcessingError("MP not recognized".to_string())) // Using existing variant, or add RecognitionFailed
            }
            Err(e) => {
                error!("Error during MP digit recognition: {}", e);
                Err(e)
            }
        }
    }

    /// Main loop for monitoring player stats.
    pub fn run_monitoring_loop(&self, deps: &AllDependencies) { // deps is now used
        info!("Player monitoring loop started.");
        while self.game_context.check_is_running() {
            match self.read_hp_from_screen(deps) { // Pass deps
                Ok(hp) => {
                    match self.read_mp_from_screen(deps) { // Pass deps
                        Ok(mp) => {
                            // Acquire lock and update player_stats
                            match self.game_context.player_stats.lock() {
                                Ok(mut stats) => {
                                    stats.hp = hp;
                                    stats.mp = mp;
                                    debug!("Player stats updated: HP={}, MP={}", hp, mp);
                                }
                                Err(poisoned_error) => {
                                    error!("Failed to acquire lock on player_stats (monitoring loop): Mutex is poisoned. {}", poisoned_error);
                                    // Depending on strategy, might want to stop the bot or re-initialize context.
                                }
                            }
                        }
                        Err(e) => {
                            error!("Error reading MP from screen: {}", e);
                            // Handle error: log, maybe set MP to a default/unknown, or skip update.
                        }
                    }
                }
                Err(e) => {
                    error!("Error reading HP from screen: {}", e);
                    // Handle error: log, maybe set HP to a default/unknown, or skip update.
                }
            }

            thread::sleep(Duration::from_secs(1)); // Sleep for 1 second
        }
        info!("Player monitoring loop stopped because is_running is false.");
    }
}
