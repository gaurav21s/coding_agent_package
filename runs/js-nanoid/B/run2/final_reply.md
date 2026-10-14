To generate IDs using `nanoid` in a Node.js ES module environment, we use the `nanoid` package. While the standard `nanoid()` function is synchronous and highly optimized, the library also provides an asynchronous version (`nanoid/async`) for environments where non-blocking behavior is preferred.

The following program demonstrates:
1.  Generating a default-length ID (21 characters) using the asynchronous API.
2.  Generating a 10-character ID using the asynchronous API.
3.  Generating a 6-character ID using a custom alphabet of digits (`0123456789`) via `customAlphabet` (also using the asynchronous API).

### `main.mjs`

```javascript
import { nanoid } from 'nanoid/async';
import { customAlphabet } from 'nanoid/async';

async function generateIds() {
  // 1. Default-length ID (21 characters)
  const defaultId = await nanoid();

  // 2. 10-character ID
  const tenCharId = await nanoid(10);

  // 3. 6-character ID made only of digits
  const digitsAlphabet = '0123456789';
  const nanoidDigits = customAlphabet(digitsAlphabet, 6);
  const digitId = await nanoidDigits();

  // Print results
  console.log(`Default ID: ${defaultId} (Length: ${defaultId.length})`);
  console.log(`10-char ID: ${tenCharId} (Length: ${tenCharId.length})`);
  console.log(`6-digit ID: ${digitId} (Length: ${digitId.length})`);
}

generateIds().catch(console.error);
```

### How to run:
1. Ensure you have `nanoid` installed:
   ```bash
   npm install nanoid
   ```
2. Run the script:
   ```bash
   node main.mjs
   ```