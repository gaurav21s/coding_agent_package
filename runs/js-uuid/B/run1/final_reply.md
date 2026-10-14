To generate UUIDs using the `uuid` package in a Node.js ES module, you can import the `v4`, `v7`, `validate`, and `version` functions directly from the package.

The following program generates a version 4 (random) UUID and a version 7 (time-ordered) UUID, validates them, and prints their detected versions.

```javascript
import { v4 as uuidv4, v7 as uuidv7, validate as uuidValidate, version as uuidVersion } from 'uuid';

/**
 * Generates and validates UUIDs, printing their version.
 */
function run() {
  // Generate UUIDs
  const v4Uuid = uuidv4();
  const v7Uuid = uuidv7();

  const uuids = [
    { label: 'Version 4 (Random)', value: v4Uuid },
    { label: 'Version 7 (Time-ordered)', value: v7Uuid }
  ];

  uuids.forEach(({ label, value }) => {
    // Validate the UUID
    const isValid = uuidValidate(value);
    
    if (isValid) {
      // Detect the version
      const detectedVersion = uuidVersion(value);
      console.log(`${label}: ${value} (Detected Version: ${detectedVersion})`);
    } else {
      console.error(`${label}: ${value} is INVALID.`);
    }
  });
}

run();
```

### How to run:
1. Ensure you have Node.js installed.
2. Initialize a project and install the `uuid` package:
   ```bash
   npm init -y
   npm install uuid
   ```
3. Save the code above as `main.mjs`.
4. Run the program:
   ```bash
   node main.mjs
   ```