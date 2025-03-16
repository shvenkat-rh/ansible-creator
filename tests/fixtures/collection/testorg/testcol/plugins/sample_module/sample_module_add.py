# sample_module.py
# GNU General Public License v3.0+

DOCUMENTATION = """
    module: sample_module
    author: Your Name (@username)
    version_added: "1.0.0"
    short_description: A custom module plugin for Ansible.
    description:
      - This is a custom module plugin
    options:
      prefix:
        description:
          - A string that is added as a prefix to the message passed to the module.
        type: str
      msg:
        description: The message to display in the output.
        type: str
      with_prefix:
        description:
          - A boolean flag indicating whether to include the prefix in the message.
        type: bool
    notes:
      - This is a scaffold template. Customize the plugin to fit your needs.
"""

EXAMPLES = """
- name: Example Module Plugin
  hosts: localhost
  tasks:
    - name: Example sample_module plugin
      with_prefix:
        prefix: "Hello, World"
        msg: "Ansible!"
"""
