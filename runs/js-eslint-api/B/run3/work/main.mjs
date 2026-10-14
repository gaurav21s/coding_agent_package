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
