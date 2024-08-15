from collections import deque

# Utilize AhoCorasic scanning for pattern recognition w/ wildcards.
class AhoCorasickWithWildcards:
    WILDCARD = '?'

    class TrieNode:
        def __init__(self):
            self.children = {}
            self.fail = None
            self.pattern_indexes = []

    def __init__(self):
        self.root = self.TrieNode()
        self.patterns = []

    def add_pattern(self, pattern):
        node = self.root
        pattern_index = len(self.patterns)
        self.patterns.append(pattern)

        i = 0
        while i < len(pattern):
            if pattern[i:i + 2] == self.WILDCARD * 2:
                char = self.WILDCARD
                i += 1  # Move by 1 for wildcards
            else:
                char = pattern[i:i + 2]
                i += 2  # Move by 2 for regular hex pairs

            if char not in node.children:
                node.children[char] = self.TrieNode()
            node = node.children[char]

        node.pattern_indexes.append(pattern_index)

    def build_failure_links(self):
        queue = deque()

        for child in self.root.children.values():
            child.fail = self.root
            queue.append(child)

        while queue:
            node = queue.popleft()

            for char, child in node.children.items():
                failure = node.fail
                while failure and char not in failure.children and self.WILDCARD not in failure.children:
                    failure = failure.fail

                if failure:
                    child.fail = failure.children.get(char) or failure.children.get(self.WILDCARD)
                else:
                    child.fail = self.root

                if child.fail:
                    child.pattern_indexes.extend(child.fail.pattern_indexes)

                queue.append(child)

    def search(self, file_content):
        matches = []
        node = self.root

        hex_content = self._file_content_to_hex(file_content)

        i = 0
        while i < len(hex_content):
            char = hex_content[i:i + 2]
            i += 2

            while node and char not in node.children and self.WILDCARD not in node.children:
                node = node.fail

            if not node:
                node = self.root
                continue

            node = node.children.get(char) or node.children.get(self.WILDCARD)

            if node:
                matches.extend(node.pattern_indexes)

        return matches

    # Convert contents to properly formatted hex.
    def _file_content_to_hex(self, file_content):
        return ''.join(f'{byte:02X}' for byte in file_content)

    def scan_file(self, file_path):
        with open(file_path, 'rb') as f:
            file_bytes = f.read()

        pattern_indexes = self.search(file_bytes)
        found_patterns = [self.patterns[index] for index in pattern_indexes]
        return found_patterns


# Example usage
if __name__ == '__main__':
    scanner = AhoCorasickWithWildcards()

    # Add patterns (as hex strings with or without wildcards)

    scanner.add_pattern('4D5A90??')  # Example with wildcards
    scanner.add_pattern('87CB486172924D')  # Example witout wildcards
    
    # Build failure links
    scanner.build_failure_links()

    # Scan a sample file
    matches = scanner.scan_file('filepath here')

    for match in matches:
        print(f"Found signature: {match}")
