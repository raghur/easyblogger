import pypandoc
converted = pypandoc.convert_file(
    "test.md", 'html',
    filters=["c:/users/raghuramanr/AppData/Roaming/npm/mermaid-filter.cmd"])
print(converted)
