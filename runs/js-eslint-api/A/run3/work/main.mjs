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
