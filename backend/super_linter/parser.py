import json
import os

class SuperLinterParser:
    def __init__(self, log_file_path):
        """
        Initializes the parser with the path to the Super Linter JSON report.
        In the cloud, this will usually be a file generated in the workspace.
        """
        self.log_file_path = log_file_path

    def parse_errors(self):
        """
        Reads the JSON report and extracts the exact file paths, 
        line numbers, and error messages.
        
        Returns:
            A list of dictionaries containing the parsed error data.
        """
        if not os.path.exists(self.log_file_path):
            print(f"❌ Parser Error: Log file not found at {self.log_file_path}")
            return []

        parsed_errors = []
        
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                # Super Linter can output standard ESLint/JSON style reports.
                # We will parse the array of file errors.
                report_data = json.load(f)
                
            # Iterate through the files that were scanned
            for file_data in report_data:
                file_path = file_data.get('filePath')
                messages = file_data.get('messages', [])
                
                for msg in messages:
                    # We only care about actual errors, not just warnings
                    if msg.get('severity') == 2: # In many linters, 2 = Error, 1 = Warning
                        error_entry = {
                            "file_path": file_path,
                            "line": msg.get('line', 1),
                            "error_rule": msg.get('ruleId', 'unknown_rule'),
                            "error_msg": msg.get('message', 'No message provided')
                        }
                        parsed_errors.append(error_entry)
                        
            print(f"✅ Parser found {len(parsed_errors)} critical errors.")
            return parsed_errors

        except Exception as e:
            print(f"❌ Failed to parse Super Linter logs: {e}")
            return []

if __name__ == "__main__":
    # Quick local test block
    print("SuperLinterParser loaded.")