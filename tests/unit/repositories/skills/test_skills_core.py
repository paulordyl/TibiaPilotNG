import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from src.repositories.skills import core as skills_core # Path to the module
from src.shared.typings import GrayImage, BBox # BBox might be needed

class TestSkillsCore(unittest.TestCase):

    def setUp(self):
        # Create a dummy screenshot for tests, can be reused
        self.dummy_screenshot: GrayImage = np.zeros((200, 200), dtype=np.uint8)
        self.dummy_skills_icon_bbox: BBox = (50, 50, 20, 20) # x, y, w, h

    @patch('src.repositories.skills.core.skb_rust_utils')
    def test_getSkillsIconPosition(self, mock_skb_rust_utils):
        mock_skb_rust_utils.get_skills_icon_roi.return_value = self.dummy_skills_icon_bbox
        
        result = skills_core.getSkillsIconPosition(self.dummy_screenshot)
        
        mock_skb_rust_utils.get_skills_icon_roi.assert_called_once()
        # Check that the first argument to the mocked function was a NumPy array
        called_arg = mock_skb_rust_utils.get_skills_icon_roi.call_args[0][0]
        self.assertIsInstance(called_arg, np.ndarray)
        self.assertEqual(result, self.dummy_skills_icon_bbox)

    @patch('src.repositories.skills.core.skb_rust_utils')
    def test_getSkillsIconPosition_not_found(self, mock_skb_rust_utils):
        mock_skb_rust_utils.get_skills_icon_roi.return_value = None
        
        result = skills_core.getSkillsIconPosition(self.dummy_screenshot)
        self.assertIsNone(result)

    # Example for getHp - similar tests would be needed for getMana, getCapacity, etc.
    @patch('src.repositories.skills.core.skb_rust_utils')
    def test_getHp(self, mock_skb_rust_utils):
        # Mock the chain: get_skills_icon_roi -> get_hp
        mock_skb_rust_utils.get_skills_icon_roi.return_value = self.dummy_skills_icon_bbox
        mock_skb_rust_utils.get_hp.return_value = 150 # Expected HP value
        
        result = skills_core.getHp(self.dummy_screenshot)
        
        mock_skb_rust_utils.get_skills_icon_roi.assert_called_once_with(
            unittest.mock.ANY # The screenshot might be a processed version
        )
        mock_skb_rust_utils.get_hp.assert_called_once_with(
            unittest.mock.ANY, # Processed screenshot
            self.dummy_skills_icon_bbox
        )
        self.assertEqual(result, 150)

    @patch('src.repositories.skills.core.skb_rust_utils')
    def test_getHp_icon_not_found(self, mock_skb_rust_utils):
        mock_skb_rust_utils.get_skills_icon_roi.return_value = None # Simulate icon not found
        
        result = skills_core.getHp(self.dummy_screenshot)
        
        self.assertIsNone(result)
        mock_skb_rust_utils.get_hp.assert_not_called() # Rust get_hp should not be called

    @patch('src.repositories.skills.core.skb_rust_utils')
    def test_getHp_hash_not_found_in_rust(self, mock_skb_rust_utils):
        mock_skb_rust_utils.get_skills_icon_roi.return_value = self.dummy_skills_icon_bbox
        mock_skb_rust_utils.get_hp.return_value = None # Simulate Rust not finding the hash
        
        result = skills_core.getHp(self.dummy_screenshot)
        
        self.assertIsNone(result)
        mock_skb_rust_utils.get_hp.assert_called_once()

    # Add similar tests for getMana, getCapacity, getSpeed, getFood, getStamina
    # Example for getFood (which might use a different hash map in Rust)
    @patch('src.repositories.skills.core.skb_rust_utils')
    def test_getFood(self, mock_skb_rust_utils):
        mock_skb_rust_utils.get_skills_icon_roi.return_value = self.dummy_skills_icon_bbox
        mock_skb_rust_utils.get_food.return_value = 30 # Expected food time in minutes
        
        result = skills_core.getFood(self.dummy_screenshot)
        
        mock_skb_rust_utils.get_skills_icon_roi.assert_called_once_with(unittest.mock.ANY)
        mock_skb_rust_utils.get_food.assert_called_once_with(
            unittest.mock.ANY, 
            self.dummy_skills_icon_bbox
        )
        self.assertEqual(result, 30)

if __name__ == '__main__':
    unittest.main()
