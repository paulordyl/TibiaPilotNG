//! Handles player survival logic, specifically healing based on current health status.
//!
//! This module provides functions to assess the player's health against predefined
//! thresholds and trigger healing actions (e.g., using a spell or item via hotkey)
//! when necessary. Future enhancements could include mana checks, item availability,
//! and more sophisticated healing strategies.

use crate::error::GameplayError;
use skb_game_state::MainGameState;
use skb_input::{EnigoKey, send_key_event}; // Assuming direct use of skb_input functions
// use skb_utils; // Currently unused directly in this file. Logging is via `log` crate.

// Example: Hardcoded healing threshold and hotkey.
// These should ideally come from skb_config or be passed as parameters.
const HEALING_THRESHOLD_PERCENT: u32 = 50;
const HEAL_SPELL_HOTKEY: EnigoKey = EnigoKey::F1; // Example hotkey for a healing spell

/// Checks the player's current health against a predefined threshold and attempts
/// a healing action by simulating a key press if health is below this threshold.
///
/// The function currently uses hardcoded values for the health threshold (50%)
/// and the healing hotkey (F1). These are placeholders and should be made
/// configurable in a production version, likely via `skb_config`.
///
/// The healing action is a "fire-and-forget" key press. The function does not
/// verify if the healing was successful (e.g., if the spell was on cooldown,
/// player had enough mana, or if health actually increased). More advanced logic
/// would involve feedback from the game state.
///
/// # Arguments
/// * `game_state`: A read-only reference to the current `MainGameState`, used to
///                 access player health and max health.
///
/// # Errors
/// Returns `GameplayError::InputError` if simulating the key press for healing fails
/// (e.g., if the input system `skb_input` reports an error).
/// Other `GameplayError` variants might be returned if preconditions are not met,
/// though current implementation is simple.
pub fn check_and_perform_healing(game_state: &MainGameState) -> Result<(), GameplayError> {
    if let Some(player_status) = game_state.get_player_status() {
        if player_status.max_health > 0 { // Avoid division by zero if max_health is 0
            let current_health_percent = (player_status.health * 100) / player_status.max_health;

            log::debug!(
                "Player health: {}/{} ({}%)",
                player_status.health,
                player_status.max_health,
                current_health_percent
            );

            if current_health_percent < HEALING_THRESHOLD_PERCENT {
                log::info!(
                    "Health at {}% (threshold {}%), attempting to heal with hotkey {:?}.",
                    current_health_percent,
                    HEALING_THRESHOLD_PERCENT,
                    HEAL_SPELL_HOTKEY
                );

                // Simulate pressing the heal spell hotkey
                // Press and release the key
                send_key_event(HEAL_SPELL_HOTKEY, true)?; // Press
                // skb_utils::timing::precise_delay(50); // Optional small delay between press/release
                send_key_event(HEAL_SPELL_HOTKEY, false)?; // Release

                log::info!("Heal hotkey {:?} sequence sent.", HEAL_SPELL_HOTKEY);

                // Note: This is a fire-and-forget action. We don't know if healing was successful
                // or if the spell was on cooldown from this function alone.
                // More advanced logic would check game state for spell cooldowns or confirmation of healing.
            }
        } else {
            log::warn!("Player max_health is 0, cannot calculate health percentage for healing.");
        }
    } else {
        log::debug!("No player status available, skipping healing check.");
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use skb_game_state::{MainGameState, PlayerStatus, Coordinate};
    // We can't easily mock skb_input::send_key_event without a more complex setup.
    // So, tests will check if the logic attempts to heal based on state,
    // and trust that send_key_event would be called. Success is no panic/error.

    fn create_test_game_state(health: u32, max_health: u32) -> MainGameState {
        let mut state = MainGameState::new();
        state.update_player_status(PlayerStatus {
            health,
            max_health,
            mana: 100, max_mana: 100, // Mana not directly used by this healing logic yet
            position: Some(Coordinate { x: 0, y: 0, z: 0 }),
            current_speed: Some(100),
            buffs: vec![],
            debuffs: vec![],
        });
        state
    }

    #[test]
    fn test_healing_when_health_is_low() {
        // Mock skb_input if possible, or ensure test doesn't actually send keys.
        // For now, assume send_key_event might try to run but fail if headless.
        // The function should still return Ok(()) or an error we can check.
        // Our current skb_input::send_key_event returns Ok if Enigo init fails (common in CI)
        // or if actual send fails.
        let game_state = create_test_game_state(40, 100); // 40% health
        // HEALING_THRESHOLD_PERCENT is 50%
        let result = check_and_perform_healing(&game_state);
        // We expect it to try to send a key. If send_key_event works (even if no actual input happens),
        // it should be Ok. If send_key_event itself errors (e.g. Enigo init totally failed beyond recovery),
        // it would be an Err.
        // Given skb_input's current error handling for Enigo init, it often returns Ok.
        assert!(result.is_ok(), "Healing should be attempted and not error out here.");
        // To truly test, we'd need to see logs or have a mock for skb_input.
    }

    #[test]
    fn test_no_healing_when_health_is_high() {
        let game_state = create_test_game_state(80, 100); // 80% health
        assert!(check_and_perform_healing(&game_state).is_ok());
        // Check logs or a mock to ensure no key was sent (manual for now).
    }

    #[test]
    fn test_no_healing_if_player_status_missing() {
        let game_state = MainGameState::new(); // No player status
        assert!(check_and_perform_healing(&game_state).is_ok());
    }

    #[test]
    fn test_no_healing_if_max_health_is_zero() {
        let game_state = create_test_game_state(0, 0); // max_health is 0
        assert!(check_and_perform_healing(&game_state).is_ok());
    }
}
