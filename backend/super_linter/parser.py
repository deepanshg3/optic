import os

class SuperLinterParser:
    def __init__(self, log_file_path):
        """
        Initializes the parser with the path to the Super Linter text log.
        """
        self.log_file_path = log_file_path

    def parse_errors(self):
        if not os.path.exists(self.log_file_path):
            print(f"❌ Parser Error: Log file not found at {self.log_file_path}")
            return []

        print(f"📄 Reading text log from: {self.log_file_path}")

        try:
            with open(self.log_file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            print(f"❌ Failed to read log file: {e}")
            return []

        errors = []
        current_file = None
        is_capturing = False
        current_error_block = ""

        for line in lines:
            # 1. Grab the file path from the log right before the error hits
            if "File:[/github/workspace/" in line:
                current_file = line.split("File:[/github/workspace/")[1].split("]")[0].strip()

            # 2. Start capturing when we see the red error flag
            if "[ERROR]" in line and "Found errors in" in line:
                is_capturing = True
            
            if is_capturing:
                current_error_block += line
                
                # 3. Stop capturing at the end of the error block
                if "[INFO]" in line and "----------------------------------------------" in line:
                    is_capturing = False
                    
                    # 4. Package it back into the exact Dictionary format healer.py expects!
                    if current_file:
                        errors.append({
                            "file_path": current_file,
                            "error_msg": current_error_block
                        })
                    current_error_block = ""

        if errors:
            print(f"✅ Parser successfully extracted {len(errors)} broken files.")
            return errors
        else:
            print("✅ No errors found in the parsed text log.")
            return []

if __name__ == "__main__":
    print("SuperLinter text parser loaded.")