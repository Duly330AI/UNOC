#!/usr/bin/env python
"""Fix test_provisioning_service.py"""

with open('backend/tests/test_provisioning_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all the broken validate_upstream insertions
content = content.replace(',`n        validate_upstream=False,', ',\n        validate_upstream=False,')

with open('backend/tests/test_provisioning_service.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed test_provisioning_service.py")
