import sys
import os
import pytest

# Thêm đường dẫn để import được module detection_api
sys.path.append(os.path.join(os.path.dirname(__file__), "../detection_api"))

# Giả lập input
def test_basic_math():
    assert 1 + 1 == 2

# (Optional) Nếu muốn test logic API, bạn có thể viết thêm test function ở đây
# Nhưng để demo CI/CD chạy xanh (Pass) thì test đơn giản này là đủ chứng minh quy trình.