To lint code using the modern ESLint Node.js API (v9.x+), we use the `ESLint` class with a "Flat Config" object. This approach avoids deprecated APIs like `CLIEngine` or the `linter` object.

The following program initializes an `ESLint` instance with the requested rules (`no-var` and `eqeqeq`) and processes the provided code string.

```javascript
import { ESLint } from "eslint";

/**
 * Linting code using the modern ESLint Flat Config API.
 * Rules:
 * - no-var: "error"
 * - eqeqeq: "error"
 */
async function runLint() {
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

  const code = "var x = 1; if (x == 2) {}";
  
  // lintText returns an array of LintResult objects
  const results = await eslint.lintText(code);

  // Iterate through results and print ruleId and line number
  for (const result of results) {
    for (const message of result.messages) {
      console.log(`Rule: ${message.ruleId}, Line: ${message.line}`);
    }
  }
}

runLint().catch((error) => {
  console.error(error);
  process.exit(1);
});
```