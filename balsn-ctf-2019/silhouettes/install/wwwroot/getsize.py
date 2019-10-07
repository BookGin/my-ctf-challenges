import sys, imageio
assert imageio.__version__ == '2.5.0'
print('(w, h) =', imageio.imread(sys.argv[1]).shape[:2])
