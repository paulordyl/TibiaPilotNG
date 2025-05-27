use log::debug;
use std::{
    collections::HashMap,
    sync::{Arc, Mutex}, // Use Arc for shared ownership if cache is used across threads extensively
};

// The cache will store the template name and its last known bounding box.
#[derive(Debug, Clone)] // Clone is useful if we want to pass copies of the cache around, though Arc<Mutex<...>> is better for sharing
pub struct DetectionCache {
    // Arc allows multiple owners, Mutex provides interior mutability safely across threads.
    // If the cache is only ever accessed by one thread or passed around mutably, Arc might be overkill.
    // However, for a system like a bot, concurrent access is a common scenario.
    cache: Arc<Mutex<HashMap<String, (i32, i32, u32, u32)>>>,
}

impl DetectionCache {
    /// Creates a new, empty DetectionCache.
    pub fn new() -> Self {
        debug!("Initializing new DetectionCache.");
        DetectionCache {
            cache: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    /// Retrieves the last known location of a template.
    /// Returns `Some((x, y, width, height))` if the template is in the cache, `None` otherwise.
    pub fn get(&self, template_name: &str) -> Option<(i32, i32, u32, u32)> {
        let cache_lock = self.cache.lock().unwrap_or_else(|poisoned| {
            // In case of a poisoned mutex, we might want to panic or re-initialize.
            // For simplicity, we'll just get the lock, but this is a point for robust error handling.
            debug!("Mutex was poisoned, recovering. Template: {}", template_name);
            poisoned.into_inner()
        });
        
        match cache_lock.get(template_name) {
            Some(&location) => {
                debug!("Cache hit for template '{}': {:?}", template_name, location);
                Some(location)
            }
            None => {
                debug!("Cache miss for template '{}'", template_name);
                None
            }
        }
    }

    /// Updates or inserts the location of a template in the cache.
    pub fn update(&self, template_name: String, location: (i32, i32, u32, u32)) {
        let mut cache_lock = self.cache.lock().unwrap_or_else(|poisoned| {
            debug!("Mutex was poisoned while trying to update template: {}", template_name);
            poisoned.into_inner()
        });
        debug!("Updating cache for template '{}' with location {:?}", template_name, location);
        cache_lock.insert(template_name, location);
    }

    /// Clears a specific template from the cache.
    #[allow(dead_code)] // Potentially useful later
    pub fn clear_template(&self, template_name: &str) {
        let mut cache_lock = self.cache.lock().unwrap_or_else(|poisoned| {
            debug!("Mutex was poisoned while trying to clear template: {}", template_name);
            poisoned.into_inner()
        });
        if cache_lock.remove(template_name).is_some() {
            debug!("Cleared template '{}' from cache.", template_name);
        } else {
            debug!("Attempted to clear template '{}', but it was not in cache.", template_name);
        }
    }

    /// Clears all entries from the cache.
    #[allow(dead_code)] // Potentially useful later
    pub fn clear_all(&self) {
        let mut cache_lock = self.cache.lock().unwrap_or_else(|poisoned| {
            debug!("Mutex was poisoned while trying to clear all cache.");
            poisoned.into_inner()
        });
        cache_lock.clear();
        debug!("Cleared all entries from cache.");
    }
}

// Default implementation for DetectionCache
impl Default for DetectionCache {
    fn default() -> Self {
        Self::new()
    }
}
