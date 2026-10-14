To use `nanoid` in a modern Node.js environment, we use the `nanoid` package (version 5.0.9 as of October 2026). The library provides an asynchronous `nanoid` function for the default implementation and a `customAlphabet` function for specific requirements.

Since `nanoid` is an ES module, we ensure the file extension is `.mjs` and use top-level `await` to handle the asynchronous generation.

```javascript
import { nanoid } from 'nanoid';
import { customAlphabet } from 'nanoid';

/**
 * As per nanoid documentation:
 * - nanoid() generates a 21-character URL-friendly ID.
 * - nanoid(size) generates an ID of a specific length.
 * - customAlphabet(alphabet, size) creates a generator for specific constraints.
 */

async function run() {
    // 1. Default-length ID (21 characters)
    const defaultId = await nanoid();

    // 2. 10-character ID
    const tenCharId = await nanoid(10);

    // 3. 6-character ID made only of digits
    const digits = '0123456789';
    const nanoidDigits = customAlphabet(digits, 6);
    const customId = await nanoidDigits();

    // Output results
    const results = [
        { label: 'Default ID', id: defaultId },
        { label: '10-char ID', id: tenCharId },
        { label: '6-digit ID', id: customId }
    ];

    results.forEach(item => {
        console.log(`${item.label}: ${item.id} (Length: ${item.id.length})`);
    });
}

// Execute the async function
await run();
```