# CACH Challenge Backend

## API methods

### `getDefinition`

Takes a comma-separated list of words and returns a JSON with the words and definitions from Wiktionary. If the word does not have an entry on Wiktionary, the `definition` field for that word is an empty string and the returned response has the code 400 (Bad Request).

Usage: `.../api/getDefinition/word1,word2,word3`

Output:

```json
{
    "word1": { "definition": "def1" },
    "word2": { "definition": "def2" },
    "word3": { "definition": "def3" }
}
```

### `getQuestion`

Takes an optional URL parameter `count` and generates that many number of questions.

Usage: `.../api/getQuestion[?count=n]`

Output:

```json
{
    "0" : {
        "answer": 1,
        "definition": "Definition of word1.",
        "options": ["word0", "word1", "word2", "word3"]
    }
}
```