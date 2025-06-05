import time
import logging
from src.gameplay.core.tasks.common.base import BaseTask # Adjusted import
from src.gameplay.typings import Context
from src.utils.keyboard import write, press

class ExecuteSpellSequenceTask(BaseTask): # Inherit from BaseTask
    def __init__(self, sequenceLabel: str):
        super().__init__() # Call BaseTask's __init__
        self.name = 'executeSpellSequence'
        self.sequenceLabel = sequenceLabel
        self.current_spell_action_index = 0
        # self.finished is inherited from BaseTask and defaults to False

    # Note: The run method in BaseTask might have a different signature or purpose.
    # This task assumes it's called repeatedly and manages its own state via current_spell_action_index.
    def do(self, context: Context) -> Context: # Changed 'run' to 'do' if BaseTask uses 'do'
        if self.sequenceLabel not in context['ng_spellSequences']:
            logging.error(f"Spell sequence label '{self.sequenceLabel}' not found in defined sequences.")
            self.finished = True
            return context

        spell_actions = context['ng_spellSequences'][self.sequenceLabel]

        if self.current_spell_action_index >= len(spell_actions):
            logging.info(f"Finished spell sequence: {self.sequenceLabel}")
            self.finished = True
            return context

        spell_action = spell_actions[self.current_spell_action_index]

        spell_name_for_log = spell_action.get('name', 'Unknown Spell') # Use .get for safer access
        spell_words = spell_action['words']
        target_type = spell_action['target_type']
        target_value = spell_action.get('target_value')
        delay_ms = spell_action['delay_ms']

        # Basic Targeting Logic (expand as needed)
        formatted_words = spell_words # Default to original words
        if target_type in ["player_name", "creature_name"] and target_value:
            # This simple replacement assumes spell_words contains "%s" for the target.
            # More robust templating might be needed if spells have varied formats.
            if '"%s"' in spell_words:
                 formatted_words = spell_words.replace('"%s"', f'"{target_value}"')
            elif '%s' in spell_words:
                 formatted_words = spell_words.replace('%s', target_value)
            # If no placeholder, the targeting system might need to be more complex,
            # or the words are used as-is and targeting is implicit (e.g. for runes on current_target).

        logging.info(f"Executing spell action {self.current_spell_action_index + 1}/{len(spell_actions)} in sequence '{self.sequenceLabel}': {spell_name_for_log} ({formatted_words})")

        # TODO: This should ideally use the Arduino/keyboard utility from the project context if available,
        #       rather than directly calling pyautogui via src.utils.keyboard for better testability and control.
        #       For now, using the provided keyboard utilities.
        write(formatted_words)
        press('enter')

        # Handle delay
        # The BaseTask system might have its own way of handling delays/durations.
        # If a task's 'do' method is expected to be quick, this time.sleep is problematic.
        # If 'do' can block, this is fine.
        # For now, assuming it can block for the purpose of this subtask.
        if delay_ms > 0:
            delay_s = delay_ms / 1000.0
            time.sleep(delay_s)

        self.current_spell_action_index += 1

        # Check if the sequence is now complete
        if self.current_spell_action_index >= len(spell_actions):
            logging.info(f"Completed all spell actions in sequence: {self.sequenceLabel}")
            self.finished = True
        else:
            # Task is not finished, it will run again for the next spell action.
            # The orchestrator needs to re-run this task until self.finished is True.
            self.finished = False

        return context
