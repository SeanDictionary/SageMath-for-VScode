# Build

**All development is recommended to be done on a Linux system.**

Install node.js and npm.

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

Install sage-lsp-server.

```bash
git clone https://github.com/SeanDictionary/sage-lsp-server
./src/server/envLSP/bin/pip install -e ./sage-lsp-server
```

