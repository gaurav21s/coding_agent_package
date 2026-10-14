import { z } from 'zod';

// 1. Define the signup schema
const signupSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  age: z.number().int().min(13).optional(),
});

// 2. Define the admin schema by extending the signup schema
const adminSchema = signupSchema.extend({
  role: z.enum(['admin', 'user']),
});

// --- Parsing Logic ---

const validData = {
  email: "test@example.com",
  password: "securePassword123",
  age: 25,
};

const invalidData = {
  email: "not-an-email",
  password: "short",
  age: 10, // Too young
};

console.log("--- Parsing Valid Data ---");
const validResult = signupSchema.safeParse(validData);
console.log("Success:", validResult.success);
console.log("Data:", validResult.data);

console.log("\n--- Parsing Invalid Data ---");
const invalidResult = signupSchema.safeParse(invalidData);

if (!invalidResult.success) {
  console.log("Validation failed. Issues:");
  
  // Print every issue's path and message
  invalidResult.error.issues.forEach((issue) => {
    console.log(`- Path [${issue.path.join('.')}]: ${issue.message}`);
  });

  // Print errors grouped per field
  console.log("\nErrors grouped per field:");
  console.log(invalidResult.error.flatten().fieldErrors);
}

console.log("\n--- Parsing Admin Data ---");
const adminData = {
  email: "admin@example.com",
  password: "adminPassword123",
  role: "admin",
};

const adminResult = adminSchema.safeParse(adminData);
console.log("Admin Success:", adminResult.success);
console.log("Admin Data:", adminResult.data);
