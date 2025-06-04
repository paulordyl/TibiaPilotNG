//! Manages combat-related decision making, including target selection and attacking.
//!
//! This module contains the logic for identifying hostile targets and initiating
//! attacks. Current implementation is a proof-of-concept and relies on hardcoded
//! values and simple strategies. Future improvements should include configurable
//! attack patterns, more sophisticated targeting, and better integration with
//! game state updates for target status.

use crate::error::GameplayError;
use skb_game_state::{MainGameState, GameEntity, EntityType};
use skb_input::{EnigoKey, send_key_event}; // Removed unused click_mouse, move_mouse_abs, EnigoMouseButton for now

// Example: Hardcoded attack hotkey or logic.
// These should ideally come from skb_config or be passed as parameters.
const ATTACK_HOTKEY: EnigoKey = EnigoKey::Space; // Example: Spacebar for attack
// const TARGET_NEXT_ENEMY_HOTKEY: EnigoKey = EnigoKey::Tab; // Example for a "target next" key

/// Handles the main combat sequence: selecting a target (if none currently exists)
/// and then attacking the current target.
///
/// This is a proof-of-concept implementation with several limitations:
/// - Target selection via `find_best_hostile_target` is very basic (picks the first
///   live, hostile monster from visible entities).
/// - The function currently only *logs* the intent to target a new entity if no
///   current target is set in `game_state`. It does not modify `game_state` to
///   set the new target, nor does it simulate an in-game targeting action (like
///   pressing Tab or clicking). This means if `game_state.get_current_target()` is `None`,
///   it might find a target, log it, but then not attack because the state wasn't updated.
/// - Attack action is a hardcoded hotkey (Spacebar) press-and-release.
/// - It does not consider player resources (e.g., mana for spells), range to target,
///   or specific attack types.
///
/// # Arguments
/// * `game_state`: A read-only reference to the current `MainGameState`. This is used
///                 to check current target, visible entities, and combat status.
///
/// # Errors
/// Returns `GameplayError::InputError` if simulating the attack key press fails.
/// Can also return `Ok(())` without action if no targets are found or if combat
/// status in `game_state` is false (though this check is currently commented out).
pub fn handle_combat_logic(game_state: &MainGameState) -> Result<(), GameplayError> {
    if !game_state.get_combat_status().unwrap_or(false) {
        // If not in combat (according to game_state), perhaps we shouldn't try to fight.
        // Or, this logic could be what SETS combat status to true.
        // For now, let's assume this function is called when combat is desired or active.
        // log::debug!("Not in combat, skipping combat logic.");
        // return Ok(());
    }

    // 1. Target Selection Logic (Very Basic)
    let current_target_id = game_state.get_current_target().map(|t| t.id);
    let mut new_target_selected_this_tick = false;

    if current_target_id.is_none() {
        // No current target, try to find one.
        if let Some(hostile_target) = find_best_hostile_target(game_state.get_all_visible_entities()) {
            log::info!("New hostile target found: {} (ID: {}). Attempting to target.", hostile_target.name, hostile_target.id);
            // How to set target?
            // Option A: Bot has an internal concept of target, then uses skb_input to target in-game.
            // Option B: Game itself has a "target next enemy" key.
            // Option C: Click on the entity (requires screen coordinates from GameEntity, which it has via `position`).

            // For this PoC, let's assume we need to click the target.
            // This is a big assumption and needs screen coordinate mapping.
            // The `GameEntity.position` would need to be screen coordinates for this to work.
            // Let's simulate pressing a "target next enemy" hotkey for now as it's simpler.
            // send_key_event(TARGET_NEXT_ENEMY_HOTKEY, true)?;
            // send_key_event(TARGET_NEXT_ENEMY_HOTKEY, false)?;
            // log::info!("Pressed 'target next enemy' hotkey. Game state needs to update with new target.");

            // For now, we'll just log. Actual targeting action requires more thought on how it's done in-game.
            // The `MainGameState` would need to be updated by another system after this action.
            // This module *requests* a target change, perception modules *confirm* it.
            // Or, this module could directly call a (hypothetical) game_state.set_current_target_by_id(hostile_target.id)
            // but that's not how our current MainGameState is structured (it takes full AttackTarget).
            new_target_selected_this_tick = true; // Placeholder
             // If we had a mutable game_state, we could update it here.
             // For now, this function is read-only on game_state for targeting part.
        } else {
            log::debug!("No hostile targets found.");
            return Ok(()); // No targets, nothing to do in combat.
        }
    }

    // If we just selected a new target this tick by pressing a hotkey,
    // we might need to wait a moment for game state to reflect the new target.
    // For a PoC, we'll assume if current_target_id was None and we found one,
    // we'll proceed as if it's targeted for the attack part.
    // A more robust system would wait for GameState to update current_target.

    // 2. Attack Logic
    if let Some(target) = game_state.get_current_target() {
        // We have a target (either pre-existing or "selected" above conceptually)
        log::info!("Attacking target: {} (ID: {}, Health: {}%)", target.name, target.id, target.health_percent);

        // Simulate pressing the attack hotkey
        send_key_event(ATTACK_HOTKEY, true)?;
        // skb_utils::timing::precise_delay(50); // Optional delay
        send_key_event(ATTACK_HOTKEY, false)?;
        log::info!("Attack hotkey {:?} sequence sent.", ATTACK_HOTKEY);

        // Check if target is dead (example)
        if target.health_percent == 0 {
            log::info!("Target {} appears to be defeated.", target.name);
            // Future: Trigger looting logic. Clear target in GameState (would need mutable access or event).
        }
    } else if !new_target_selected_this_tick { // Only log "no target to attack" if we didn't just try to select one
        log::debug!("No current target to attack.");
    }

    Ok(())
}

/// Finds the "best" hostile target from a list of visible game entities.
///
/// This is a very basic implementation: it returns the first entity in the list
/// that is a `Monster`, marked as `is_hostile`, and has `health_percent > 0`.
/// Future enhancements could involve more sophisticated criteria like proximity,
/// threat level, or specific targeting priorities.
///
/// # Arguments
/// * `entities`: A slice of `GameEntity` representing currently visible entities.
///
/// # Returns
/// Returns `Some(&GameEntity)` if a suitable target is found, otherwise `None`.
fn find_best_hostile_target(entities: &[GameEntity]) -> Option<&GameEntity> {
    entities.iter().find(|e|
        e.entity_type == EntityType::Monster &&
        e.is_hostile.unwrap_or(false) &&
        e.health_percent.unwrap_or(0) > 0 // Only target live entities
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use skb_game_state::{MainGameState, GameEntity, EntityType, AttackTarget, Coordinate};

    fn create_game_state_with_entities(entities: Vec<GameEntity>, current_target: Option<AttackTarget>) -> MainGameState {
        let mut state = MainGameState::new();
        state.update_visible_entities(entities);
        if let Some(target) = current_target {
            state.set_current_target(target);
        }
        state.set_combat_status(true); // Assume combat is active for these tests
        state
    }

    #[test]
    fn test_combat_attacks_current_target() {
        let target = AttackTarget { id: 1, name: "Test Monster".to_string(), health_percent: 100 };
        let game_state = create_game_state_with_entities(vec![], Some(target.clone()));
        let result = handle_combat_logic(&game_state);
        assert!(result.is_ok());
        // Check logs or mock to verify attack hotkey was pressed for "Test Monster"
    }

    #[test]
    fn test_combat_finds_and_attacks_new_target() {
        let monster = GameEntity {
            id: 1, name: "Hostile Wolf".to_string(),
            entity_type: EntityType::Monster,
            is_hostile: Some(true),
            health_percent: Some(100),
            position: Coordinate::default(),
            is_attacking_player: Some(false),
            is_targeted_by_player: Some(false),
        };
        // Game state initially has no current target, but one hostile entity is visible
        let game_state = create_game_state_with_entities(vec![monster], None);

        // Note: Our current handle_combat_logic doesn't actually set the target in GameState.
        // It just logs "New hostile target found" and then proceeds to attack game_state.get_current_target().
        // So this test will show it found a target (logged) but then didn't attack as current_target is still None.
        // This reveals a PoC limitation.
        let result = handle_combat_logic(&game_state);
        assert!(result.is_ok());
        // To make this test more meaningful, handle_combat_logic would need to be refactored
        // or it would need mutable access to game_state to set the target.
        // For now, we're testing the current PoC implementation.
    }

    #[test]
    fn test_combat_no_action_if_no_targets() {
        let game_state = create_game_state_with_entities(vec![], None);
        let result = handle_combat_logic(&game_state);
        assert!(result.is_ok());
        // Check logs or mock to verify no attack action was taken
    }

    #[test]
    fn test_find_best_hostile_target_logic() {
        let e1 = GameEntity { id: 1, name: "Friendly NPC".to_string(), entity_type: EntityType::Npc, is_hostile: Some(false), health_percent: Some(100), ..Default::default() };
        let e2 = GameEntity { id: 2, name: "Wolf".to_string(), entity_type: EntityType::Monster, is_hostile: Some(true), health_percent: Some(100), ..Default::default() };
        let e3 = GameEntity { id: 3, name: "Dead Wolf".to_string(), entity_type: EntityType::Monster, is_hostile: Some(true), health_percent: Some(0), ..Default::default() };
        let e4 = GameEntity { id: 4, name: "Boar".to_string(), entity_type: EntityType::Monster, is_hostile: Some(true), health_percent: Some(50), ..Default::default() };

        let entities = vec![e1.clone(), e2.clone(), e3.clone(), e4.clone()];
        // Should pick e2 (first live hostile monster)
        assert_eq!(find_best_hostile_target(&entities), Some(&e2));

        let entities_only_boar_alive = vec![e1.clone(), e3.clone(), e4.clone()];
        assert_eq!(find_best_hostile_target(&entities_only_boar_alive), Some(&e4));

        let no_hostiles = vec![e1, e3]; // Friendly NPC and Dead Wolf
        assert!(find_best_hostile_target(&no_hostiles).is_none());
    }
}
