import sys
import os

current_dir = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.dirname(current_dir)
src_dir = os.path.join(root_dir, 'src')

sys.path.append(src_dir)
