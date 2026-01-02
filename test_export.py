import unittest
from unittest.mock import MagicMock, patch
import os
import json
import main
from ferry_service import FerryConnection

class TestExport(unittest.TestCase):
    @patch('main.FerryService')
    def test_export_json(self, MockService):
        # Setup mock
        mock_instance = MockService.return_value
        mock_instance.find_available.return_value = [
            FerryConnection(
                date="2026-01-02",
                departure_time="10:00",
                arrival_time="11:00",
                departure_harbor="DEWYK",
                arrival_harbor="DEDAG",
                available=True,
                only_persons=False,
                booking_url="http://example.com",
                raw_text="Example"
            )
        ]
        
        export_path = "docs/test_data.json"
        
        # Run main with export arg
        with patch('argparse.ArgumentParser.parse_args',
                   return_value=main.argparse.Namespace(export_json=export_path)):
            main.main()
            
        # Verify file created
        self.assertTrue(os.path.exists(export_path))
        
        with open(export_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.assertIn("connections", data)
        self.assertEqual(len(data["connections"]), 1)
        self.assertEqual(data["connections"][0]["date"], "2026-01-02")
        
        # Cleanup
        if os.path.exists(export_path):
            os.remove(export_path)
        print("Test passed!")

if __name__ == '__main__':
    unittest.main()
