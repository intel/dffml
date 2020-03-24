curl -sSLO "http://yann.lecun.com/exdb/mnist/{train-images-idx3,train-labels-idx1,t10k-images-idx3,t10k-labels-idx1}-ubyte.gz"
sha384sum -c - << EOF
1bf45877962fd391f7abb20534a30fd2203d0865309fec5f87d576dbdbefdcb16adb49220afc22a0f3478359d229449c  t10k-images-idx3-ubyte.gz
ccc1ee70f798a04e6bfeca56a4d0f0de8d8eeeca9f74641c1e1bfb00cf7cc4aa4d023f6ea1b40e79bb4707107845479d  t10k-labels-idx1-ubyte.gz
f40eb179f7c3d2637e789663bde56d444a23e4a0a14477a9e6ed88bc39c8ad6eaff68056c0cd9bb60daf0062b70dc8ee  train-images-idx3-ubyte.gz
ba9c11bf9a7f7c2c04127b8b3e568cf70dd3429d9029ca59b7650977a4ac32f8ff5041fe42bc872097487b06a6794e00  train-labels-idx1-ubyte.gz
EOF