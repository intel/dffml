## LLM Based Debug of Creating Policy Engine Workflow for Repo CI Validation

> What OS (/usr/lib/os-release or /etc/os-release) am I on, what's it's package manager, what does the LLM think will move us from ad-hoc CVE of install failure to VEX of not affected for this branch in train of thought

```console
$ pyenv install 3.12
Downloading Python-3.12.1.tar.xz...
-> https://www.python.org/ftp/python/3.12.1/Python-3.12.1.tar.xz
Installing Python-3.12.1...
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/home/pdxjohnny/.pyenv/versions/3.12.1/lib/python3.12/bz2.py", line 17, in <module>
    from _bz2 import BZ2Compressor, BZ2Decompressor
ModuleNotFoundError: No module named '_bz2'
WARNING: The Python bz2 extension was not compiled. Missing the bzip2 lib?
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/home/pdxjohnny/.pyenv/versions/3.12.1/lib/python3.12/curses/__init__.py", line 13, in <module>
    from _curses import *
ModuleNotFoundError: No module named '_curses'
WARNING: The Python curses extension was not compiled. Missing the ncurses lib?
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/home/pdxjohnny/.pyenv/versions/3.12.1/lib/python3.12/ctypes/__init__.py", line 8, in <module>
    from _ctypes import Union, Structure, Array
ModuleNotFoundError: No module named '_ctypes'
WARNING: The Python ctypes extension was not compiled. Missing the libffi lib?
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ModuleNotFoundError: No module named 'readline'
WARNING: The Python readline extension was not compiled. Missing the GNU readline lib?
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/home/pdxjohnny/.pyenv/versions/3.12.1/lib/python3.12/sqlite3/__init__.py", line 57, in <module>
    from sqlite3.dbapi2 import *
  File "/home/pdxjohnny/.pyenv/versions/3.12.1/lib/python3.12/sqlite3/dbapi2.py", line 27, in <module>
    from _sqlite3 import *
ModuleNotFoundError: No module named '_sqlite3'
WARNING: The Python sqlite3 extension was not compiled. Missing the SQLite3 lib?
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/home/pdxjohnny/.pyenv/versions/3.12.1/lib/python3.12/tkinter/__init__.py", line 38, in <module>
    import _tkinter # If this fails your Python may not be configured for Tk
    ^^^^^^^^^^^^^^^
ModuleNotFoundError: No module named '_tkinter'
WARNING: The Python tkinter extension was not compiled and GUI subsystem has been detected. Missing the Tk toolkit?
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/home/pdxjohnny/.pyenv/versions/3.12.1/lib/python3.12/lzma.py", line 27, in <module>
    from _lzma import *
ModuleNotFoundError: No module named '_lzma'
WARNING: The Python lzma extension was not compiled. Missing the lzma lib?
```

- user: What dnf install commands do I need to issue?

The errors you are encountering are due to missing development libraries that are required to compile the Python extensions. Here are the necessary `dnf install` commands to install these libraries on a Fedora-based system:

```bash
sudo dnf install -y bzip2-devel ncurses-devel libffi-devel readline-devel sqlite-devel tk-devel xz-devel
```

After installing these libraries, you should reconfigure and recompile Python. Here’s a complete set of steps you can follow:

1. **Install the required libraries:**

   ```bash
   sudo dnf install -y bzip2-devel ncurses-devel libffi-devel readline-devel sqlite-devel tk-devel xz-devel
   ```

2. **Reconfigure and recompile Python:**

   ```bash
   cd /path/to/Python-3.12.1
   ./configure
   make
   sudo make install
   ```

By following these steps, you should be able to successfully compile and install Python 3.12.1 with all necessary extensions.