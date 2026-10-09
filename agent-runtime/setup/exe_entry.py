"""Static PyInstaller entry; no source checkout/Python/PATH dependency."""
from agent_setup.exe_main import guarded_main

if __name__ == '__main__':
    raise SystemExit(guarded_main())
