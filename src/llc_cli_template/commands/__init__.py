"""Commands package: one small module per CLI subcommand.

Each command module contains pure-ish logic that takes a parsed data
document and returns plain values; printing and exit-code decisions live
in cli/main.py. This keeps commands testable without capturing stdout.
"""
