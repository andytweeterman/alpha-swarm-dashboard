import unittest
import os
import sys
import shutil
import base64
from unittest.mock import MagicMock

# Mock streamlit before importing styles
sys.modules['streamlit'] = MagicMock()
sys.modules['plotly'] = MagicMock()
sys.modules['plotly.graph_objects'] = MagicMock()

# Add root to path to import styles
sys.path.append(os.getcwd())
import styles

class TestStylesTraversal(unittest.TestCase):
    def setUp(self):
        # Create a fake environment in /tmp or local directory
        self.test_dir = os.path.abspath("test_env_styles")
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)

        self.fake_app_dir = os.path.join(self.test_dir, "fake_app")
        os.makedirs(self.fake_app_dir)

        self.fake_sibling_dir = os.path.join(self.test_dir, "fake_app_sibling")
        os.makedirs(self.fake_sibling_dir)

        self.secret_file = os.path.join(self.fake_sibling_dir, "secret.txt")
        with open(self.secret_file, "w") as f:
            f.write("SECRET_DATA")

        # Save original __file__
        self.original_file = styles.__file__

        # Point styles.__file__ to the fake app directory
        # This makes get_base64_image think it is running from there
        styles.__file__ = os.path.join(self.fake_app_dir, "styles.py")

    def tearDown(self):
        # Restore __file__
        styles.__file__ = self.original_file

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_directory_traversal_blocked(self):
        # Attempt to access the sibling file
        # Relative path from fake_app/styles.py to fake_app_sibling/secret.txt
        # is ../fake_app_sibling/secret.txt

        # Note: /.../fake_app_sibling starts with /.../fake_app
        # So string prefix check would fail (allow access)
        # But commonpath check should succeed (block access)

        result = styles.get_base64_image("../fake_app_sibling/secret.txt")

        self.assertIsNone(result, "Directory traversal should be blocked and return None")

    def test_valid_image_allowed(self):
        # Create a valid image in the app dir
        valid_img = os.path.join(self.fake_app_dir, "valid.png")
        with open(valid_img, "w") as f:
            f.write("valid_image_data")

        result = styles.get_base64_image("valid.png")
        self.assertIsNotNone(result)
        decoded = base64.b64decode(result).decode()
        self.assertEqual(decoded, "valid_image_data")

if __name__ == "__main__":
    unittest.main()
