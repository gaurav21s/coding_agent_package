To lint code using the `eslint` package (v9.x) via the Node.js API, you use the `ESLint` class. In version 9, the configuration is defined using the `FlatConfig` format. Since we are not reading from disk, we pass the configuration object directly to the `ESLint` constructor.

Here is the `main.mjs` file:

```javascript
import { ESLint } from "eslint";

async function runLint() {
  // Initialize ESLint with a flat config object
  // We disable all default rules and enable only the requested ones
  const eslint = new ESLint({
    overrideConfig: [
      {
        rules: {
          "no-var": "error",
          "eqeqeq": "error"
        }
      }
    ],
    useEslintrc: false, // Ensure no config files are loaded from disk
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
1.  **`ESLint` Class**: This is the primary entry point for the ESLint Node.js API in version 9.
2.  **`overrideConfig`**: This allows us to define the rules programmatically. By setting `useEslintrc: false`, we guarantee that the program ignores any `.eslintrc` or `eslint.config.js` files in the environment.
3.  **`lintText`**: This method processes the provided string.
4.  **Output**: The script iterates through the `messages` array returned by the linter and prints the `ruleId` and `line` for each violation.

To run this, ensure you have installed the latest version of eslint:
`npm install eslint`

Then execute:
`node main.mjs`