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
