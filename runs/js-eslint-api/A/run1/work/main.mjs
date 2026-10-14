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
