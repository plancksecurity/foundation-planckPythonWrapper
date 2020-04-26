# pEpPythonAdapter

## Build Insttructions

These build instructions should work on:
 * Linux (Verified 26.4.20 - heck)
 * MacOS (Verified 26.4.20 - heck)
 * Windows

### Build
To build against system wide pEp installation (libs/includes) 
```bash
python3 setup.py build_ext
```

To build against a pEp installation in your home dir (libs/includes): 
```bash
python3 setup.py build_ext --local
```

To build against a pEp installation in a custom installation root (libs/includes) 
```bash
python3 setup.py build_ext --prefix=<path_to_your_install_root>
```

### Install

To install the extension module system wide, as root, run:
```bash
python3 setup.py install
```

To install the extension module into you home dir
```bash
python3 setup.py install --user
```

To install the extension module into a custom destination
```bash
python3 setup.py install --prefix=<custom_destination_root>
```
Attention: The ~ (tilde) does not get expanded, but env vars work ($HOME). 