import { nanoid, customAlphabet } from 'nanoid';

/**
 * As per the latest nanoid documentation and changelog:
 * 1. The async API has been removed.
 * 2. The library is ESM-only.
 * 3. The default alphabet uses '-' instead of '~'.
 */

async function run() {
  // 1. Default-length ID (21 characters)
  const defaultId = nanoid();

  // 2. 10-character ID
  const tenCharId = nanoid(10);

  // 3. 6-character ID made only of digits
  const digits = '0123456789';
  const nanoidDigits = customAlphabet(digits, 6);
  const customId = nanoidDigits();

  const results = [
    { label: 'Default-length ID', id: defaultId },
    { label: '10-character ID', id: tenCharId },
    { label: '6-character digit ID', id: customId }
  ];

  results.forEach(item => {
    console.log(`${item.label}: ${item.id} (Length: ${item.id.length})`);
  });
}

run().catch(console.error);
