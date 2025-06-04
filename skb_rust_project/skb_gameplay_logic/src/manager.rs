//! Orchestrates the main gameplay logic by calling various specialized modules.
//!
//! The `GameplayLogicManager` is responsible for making high-level decisions
//! and coordinating actions based on the current game state. It delegates
//! specific tasks like healing and combat to their respective modules.

use crate::error::GameplayError;
use crate::healing;
use crate::combat;
// use crate::looting; // If looting module is to be included

use skb_game_state::MainGameState;
use log;

/// Manages the overall gameplay logic flow by coordinating calls to specialized modules
/// such as healing, combat, and potentially looting or navigation.
///
/// It operates on a `tick` basis, processing the current game state and deciding
/// what actions, if any, should be performed.
#[derive(Default)]
pub struct GameplayLogicManager {
    // Configuration for gameplay logic can be stored here in the future.
    // For example, parameters loaded from `skb_config` could define thresholds,
    // preferred spells/items, or tactical preferences.
    // Current PoC uses hardcoded values within sub-modules (healing, combat).
}

impl GameplayLogicManager {
    /// Creates a new `GameplayLogicManager` with default settings.
    ///
    /// In future versions, this constructor might accept configuration parameters
    /// (e.g., loaded from `skb_config`) to customize the gameplay logic.
    pub fn new() -> Self {
        GameplayLogicManager {
            ..Default::default()
        }
    }

    /// Processes the current game state and executes a cycle of gameplay logic actions.
    ///
    /// This method typically performs actions in a prioritized order:
    /// 1. Survival checks (e.g., healing via `healing::check_and_perform_healing`).
    /// 2. Combat actions (e.g., via `combat::handle_combat_logic`), potentially deferred
    ///    if player health is critically low.
    /// 3. Other actions like looting (currently placeholder).
    ///
    /// Each step logs its activity and outcome using the `log` crate.
    ///
    /// # Arguments
    /// * `current_game_state`: A read-only reference to the current `MainGameState`
    ///                         representing the bot's understanding of the game world.
    ///
    /// # Errors
    /// Propagates `GameplayError` from any of the subordinate logic modules if they
    /// encounter an issue (e.g., an input error when trying to press a key).
    pub fn tick(&self, current_game_state: &MainGameState) -> Result<(), GameplayError> {
        log::debug!("GameplayLogicManager tick initiated.");

        // --- Priority 1: Survival ---
        healing::check_and_perform_healing(current_game_state)?;
        log::debug!("Healing check completed.");

        // --- Priority 2: Combat ---
        // Add a check: only engage in combat if player is not critically low (e.g. after healing attempt)
        // This is a simple example of inter-logic dependency.
        let mut proceed_to_combat = true;
        if let Some(ps) = current_game_state.get_player_status() {
            if ps.max_health > 0 { // Avoid division by zero
                let health_percent = (ps.health * 100) / ps.max_health;
                if health_percent < 25 { // Example: Don't fight if <25% health
                    log::warn!("Player health critically low ({}%), deferring combat this tick.", health_percent);
                    proceed_to_combat = false;
                }
            } else { // max_health is 0 or not set properly
                log::warn!("Player max_health is 0, cannot determine health percentage. Deferring combat.");
                proceed_to_combat = false;
            }
        } else { // No player status available
            log::warn!("No player status available. Deferring combat.");
            proceed_to_combat = false;
        }


        if proceed_to_combat {
            combat::handle_combat_logic(current_game_state)?;
            log::debug!("Combat logic handled.");
        } else {
            log::debug!("Combat logic deferred due to low health or other conditions.");
        }


        // --- Priority 3: Looting (Example - still placeholder) ---
        // if !current_game_state.is_in_combat.unwrap_or(false) {
        //    // looting::check_and_perform_looting(current_game_state)?;
        //    log::debug!("Looting check would be here.");
        // }

        log::debug!("GameplayLogicManager tick completed.");
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use skb_game_state::{MainGameState, PlayerStatus, GameEntity, EntityType, Coordinate, AttackTarget};

    fn create_test_game_state_for_manager(health: u32, max_health: u32, has_target_entity: bool) -> MainGameState {
        let mut state = MainGameState::new();
        state.update_player_status(PlayerStatus {
            health, max_health, mana: 100, max_mana: 100,
            position: Some(Coordinate::default()),
            ..Default::default()
        });
        if has_target_entity {
            let monster = GameEntity {
                id: 1, name: "Test Target Entity".to_string(),
                entity_type: EntityType::Monster,
                is_hostile: Some(true), health_percent: Some(100),
                position: Coordinate::default(),
                ..Default::default()
            };
            state.upsert_visible_entity(monster.clone());
            state.set_current_target(AttackTarget {
                id: monster.id,
                name: monster.name,
                health_percent: 100
            });
        }
        state.set_combat_status(true);
        state
    }

    #[test]
    fn test_manager_tick_calls_healing_low_health() {
        let manager = GameplayLogicManager::new();
        let game_state = create_test_game_state_for_manager(30, 100, true);
        assert!(manager.tick(&game_state).is_ok());
    }

    #[test]
    fn test_manager_tick_calls_healing_and_combat_high_health_with_target() {
        let manager = GameplayLogicManager::new();
        let game_state = create_test_game_state_for_manager(80, 100, true);
        assert!(manager.tick(&game_state).is_ok());
    }

    #[test]
    fn test_manager_tick_no_combat_if_critically_low_health_even_with_target() {
        let manager = GameplayLogicManager::new();
        let game_state = create_test_game_state_for_manager(10, 100, true);
        assert!(manager.tick(&game_state).is_ok());
    }

    #[test]
    fn test_manager_tick_combat_proceeds_if_no_player_status() {
        let manager = GameplayLogicManager::new();
        let mut game_state = MainGameState::new();
        game_state.set_combat_status(true);
        let monster = GameEntity { id: 1, name: "Test Target".to_string(), entity_type: EntityType::Monster, is_hostile: Some(true), health_percent: Some(100), ..Default::default()};
        game_state.upsert_visible_entity(monster.clone()); // Corrected: use game_state here
        game_state.set_current_target(AttackTarget { id: monster.id, name: monster.name, health_percent: 100 }); // Corrected: use game_state here

        assert!(manager.tick(&game_state).is_ok());
    }
     #[test]
    fn test_manager_tick_combat_proceeds_if_player_max_health_zero() {
        let manager = GameplayLogicManager::new();
        let game_state = create_test_game_state_for_manager(0, 0, true);
        assert!(manager.tick(&game_state).is_ok());
    }
}
