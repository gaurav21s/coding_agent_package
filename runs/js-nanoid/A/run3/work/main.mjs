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
