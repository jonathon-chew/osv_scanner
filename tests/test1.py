import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "osv_scanner"))

import find_files # type: ignorec

# find_files.find("/Users/hunteradder626/Documents/Scripts/Python/Draft/osv_scanner/tests/fixtures", v=True, DEBUG=True)

find_files.find("/Users/hunteradder626/Documents/Scripts/Git/Third_Party", v=True, DEBUG=True)