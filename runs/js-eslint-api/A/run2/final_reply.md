To lint code using the `eslint` package (v9.x) via the Node.js API, we use the `ESLint` class. In version 9, the configuration is handled via the `overrideConfig` property (or the `configType: 'flat'` approach). Since we want to avoid reading files from disk, we explicitly set `useEslintrc: false`.

Here is the `main.mjs` file:

```javascript
import { ESLint } from "eslint";

async function runLint() {
  // Initialize ESLint with no config file and specific rules
  const eslint = new ESLint({
    useEslintrc: false,
    overrideConfig: [
      {
        rules: {
          "no-var": "error",
          "eqeqeq": "error"
        },
        languageOptions: {
          ecmaVersion: 2022,
          sourceType: "module"
        }
      }
    ]
  });

  const code = "var x = 1; if (x == 2) {}";

  // Lint the text
  const results = await eslint.lintText(code);

  // Process and print results
  results.forEach((result) => {
    result.messages.forEach((msg) => {
      console.log(`Rule: ${msg.ruleId}, Line: ${msg.line}`);
    });
  });
}

runLint().catch((error) => {
  console.error(error);
  process.exit(1);
});
```

### Explanation:
1.  **`ESLint` class**: This is the primary entry point for the ESLint Node.js API in version 9.
2.  **`useEslintrc: false`**: This ensures that ESLint ignores any configuration files (like `.eslintrc` or `eslint.config.js`) present in the directory.
3.  **`overrideConfig`**: This allows us to define the rules (`no-var` and `eqeqeq`) programmatically.
4.  **`languageOptions`**: Necessary to define the environment (e.g., `ecmaVersion`) so the parser understands the syntax.
5.  **`lintText`**: This method processes the provided string directly without needing a file on disk.
6.  **Output**: The script iterates through the `messages` array in the result object to extract and print the `ruleId` and `line` as requested.