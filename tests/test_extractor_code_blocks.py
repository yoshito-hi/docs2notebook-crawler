import unittest
from src.extractor import ContentExtractor

class TestContentExtractorCodeBlocks(unittest.TestCase):
    def setUp(self):
        self.extractor = ContentExtractor()

    def test_extract_code_block_without_line_numbers(self):
        # Mock HTML simulating a code block with line numbers (using select-none)
        html_content = """
        <html>
        <body>
            <main>
            <div class="code-block">
                <div class="row">
                    <div class="select-none">1</div>
                    <div class="code-content">print("First Line")</div>
                </div>
                <div class="row">
                    <div class="select-none">2</div>
                    <div class="code-content">print("Second Line")</div>
                </div>
            </div>
            
            <div class="another-block">
                 <span class="line-number">3</span>
                 <code>var x = 999;</code>
            </div>
            </main>
        </body>
        </html>
        """
        
        extracted_text = self.extractor.extract(html_content, "http://example.com")
        
        # Check that line numbers are gone
        self.assertNotIn("1", extracted_text)
        self.assertNotIn("2", extracted_text)
        self.assertNotIn("3", extracted_text)
        
        # Check that code content remains
        self.assertIn('print("First Line")', extracted_text)
        self.assertIn('print("Second Line")', extracted_text)
        self.assertIn('var x = 999;', extracted_text)

if __name__ == '__main__':
    unittest.main()
