import os

from streamlit.testing.v1 import AppTest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

at = AppTest.from_file(f"{CURRENT_DIR}/../src/main.py")
at.run(timeout=40)
assert not at.exception

# at.text_input("word").input("Bazbat").run()
# assert at.warning[0].value == "Try again."
