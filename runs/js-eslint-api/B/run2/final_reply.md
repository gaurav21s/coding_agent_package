To lint the code string `var x = 1; if (x == 2) {}` using the ESLint Node.js API, we use the `ESLint` class from the `eslint` package. Since we want to avoid reading any configuration files from the disk, we initialize the `ESLint` instance with `useEslintrc: false` and provide our custom configuration directly via the `overrideConfig` option.

The following program uses the `ESLint` class to lint the provided code string and prints the `ruleId` and `line` number for each reported error.

```javascript
import { ESLint } from "eslint";

async function runLint() {
  // Initialize ESLint with no config file and custom rules
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

  // Lint the text
  const results = await eslint.lintText(code);

  // Iterate through results and print ruleId and line number
  results.forEach((result) => {
    result.messages.forEach((msg) => {
      console.log(`ruleId: ${msg.ruleId}, line: ${msg.line}`);
    });
  });
}

runLint().catch((error) => {
  console.error(error);
  process.exit(1);
});
```

Save this code as `main.mjs` and run it using `node main.mjs`. It will output:
```text
ruleId: no-var, line: 1
ruleId: eqeqeq, line: 1
```