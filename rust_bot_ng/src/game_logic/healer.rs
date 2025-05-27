use crate::{
    game_logic::context::GameContext,
    input::{self, arduino::ArduinoCom}, // For ArduinoCom and input::keyboard
    AppError,
};
use log::{debug, info, error}; // Added error
use std::sync::{Arc, Mutex};

pub struct Healer {
    game_context: Arc<GameContext>,
    arduino_com: Arc<Mutex<ArduinoCom>>,
}

impl Healer {
    pub fn new(game_context: Arc<GameContext>, arduino_com: Arc<Mutex<ArduinoCom>>) -> Self {
        debug!("Initializing new Healer instance.");
        Healer {
            game_context,
            arduino_com,
        }
    }

    pub fn check_and_perform_heal(&self, heal_hotkey: &str) -> Result<(), AppError> {
        let player_stats = self.game_context.player_stats.lock().unwrap_or_else(|e| {
            error!("Healer: Failed to lock player_stats (poisoned): {}", e);
            // In case of poison, we might want to return a default/dummy stats or propagate error
            // For simplicity, we re-panic or return a default that won't trigger healing
            e.into_inner() 
        });
        
        let bot_settings = self.game_context.bot_settings.lock().unwrap_or_else(|e| {
            error!("Healer: Failed to lock bot_settings (poisoned): {}", e);
            e.into_inner()
        });

        let current_hp = player_stats.hp;
        let hp_threshold = bot_settings.auto_heal_hp_threshold;

        debug!(
            "Checking healing: Current HP={}, HP Threshold={}",
            current_hp, hp_threshold
        );

        if current_hp < hp_threshold {
            info!(
                "HP is low ({} < {}), attempting to heal by pressing hotkey: {}",
                current_hp, hp_threshold, heal_hotkey
            );
            match self.arduino_com.lock() {
                Ok(mut arduino_guard) => {
                    match input::keyboard::press(&mut *arduino_guard, &[heal_hotkey]) {
                        Ok(_) => {
                            info!("Successfully pressed heal hotkey: {}", heal_hotkey);
                        }
                        Err(e) => {
                            error!("Failed to press heal hotkey '{}': {}", heal_hotkey, e);
                            return Err(e); // Propagate the error from keyboard press
                        }
                    }
                }
                Err(poisoned_error) => {
                    error!(
                        "Failed to acquire lock on ArduinoCom for healing: Mutex is poisoned. {}",
                        poisoned_error
                    );
                    return Err(AppError::InputError(format!(
                        "Failed to acquire lock on ArduinoCom for healing (hotkey: {}): Mutex is poisoned. {}",
                        heal_hotkey, poisoned_error
                    )));
                }
            }
        } else {
            debug!("HP is sufficient ({} >= {}), no healing needed.", current_hp, hp_threshold);
        }
        Ok(())
    }
}
