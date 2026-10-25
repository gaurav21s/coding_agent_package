To lint code using the modern ESLint Node.js API (Flat Config), we use the `ESLint` class. Since the requirement is to avoid reading configuration files from disk, we pass a configuration object directly to the `ESLint` constructor with `useEslintrc: false`.

The following program uses the `ESLint` class to lint the provided string and outputs the `ruleId` and `line` number for each violation.

```javascript
import { ESLint } from "eslint";

/**
 * Program to lint a code string using ESLint's Flat Config API.
 * Uses the ESLint class as per the current stable API.
 */
async function runLint() {
  const code = "var x = 1; if (x == 2) {}";

  // Initialize ESLint with Flat Config
  // useEslintrc: false ensures no config files are loaded from the filesystem
  const eslint = new ESLint({
    useEslintrc: false,
    overrideConfig: [
      {
        rules: {
          "no-var": "error",
          "eqeqeq": "error"
        }
      }
    ]
  });

  try {
    // Lint the provided text
    const results = await eslint.lintText(code);

    // Iterate through results and print ruleId and line number
    results.forEach((result) => {
      result.messages.forEach((msg) => {
        console.log(`ruleId: ${msg.ruleId}, line: ${msg.line}`);
      });
    });
  } catch (error) {
    console.error("Error during linting:", error);
  }
}

runLint();
```