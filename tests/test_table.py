import sys
import os

sys.path.insert(0, os.getcwd())

import pytest
from bot_storage import event_table, read_all_events

# pytest.skip('fix this later')
# def test_table():
#     events = read_all_events('./ACMBOT.csv')
#     print()
#     print(event_table(events))

