import { createHash } from "node:crypto";
import { eq } from "drizzle-orm";
import { extractClerkId } from "../utils";
import { db } from ".";
import { checks, texts, users } from "./schema";

const generateContentHash = (content: string): string => {
  return createHash("sha256").update(content.trim()).digest("hex");
};

const calculateWordCount = (content: string): number => {
  return content.trim().split(/\s+/).length;
};

export const findOrCreateText = async (content: string) => {
  const contentHash = generateContentHash(content);
  const wordCount = calculateWordCount(content).toString();

  const existingText = await db
    .select()
    .from(texts)
    .where(eq(texts.hash, contentHash))
    .limit(1);

  if (existingText.length > 0) {
    return existingText[0];
  }

  const [newText] = await db
    .insert(texts)
    .values({
      hash: contentHash,
      content,
      wordCount,
    })
    .returning();

  return newText;
};

export const getUserById = async (userId: string) => {
  const clerkId = extractClerkId(userId);
  const [user] = await db
    .select()
    .from(users)
    .where(eq(users.id, clerkId))
    .limit(1);

  return user;
};

/**
 * Validates email format using a basic regex pattern
 */
const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validates userId format - should be non-empty string
 */
const isValidUserId = (userId: string): boolean => {
  return typeof userId === 'string' && userId.trim().length > 0;
};

/**
 * Finds an existing user or creates a new one if not found
 * @param userId - Clerk user ID
 * @param email - User's email address
 * @param imageUrl - Optional user profile image URL
 * @returns Promise resolving to the user record
 * @throws Error if input validation fails or database operation fails
 */
export const findOrCreateUser = async (userId: string, email: string, imageUrl?: string) => {
  try {
    // Input validation
    if (!isValidUserId(userId)) {
      throw new Error("Invalid userId: must be a non-empty string");
    }

    if (!isValidEmail(email)) {
      throw new Error("Invalid email format");
    }

    // Sanitize inputs
    const sanitizedEmail = email.trim().toLowerCase();
    const clerkId = extractClerkId(userId.trim());
    
    // First try to find existing user
    const existingUser = await getUserById(userId);
    if (existingUser) {
      console.log(`Found existing user: ${clerkId}`);
      return existingUser;
    }

    console.log(`Creating new user: ${clerkId} (${sanitizedEmail})`);

    // Create new user if not found
    const [newUser] = await db
      .insert(users)
      .values({
        id: clerkId,
        email: sanitizedEmail,
        imageUrl: imageUrl?.trim() || null,
      })
      .returning();

    if (!newUser) {
      throw new Error("Failed to create user: no user returned from database");
    }

    console.log(`Successfully created user: ${clerkId}`);
    return newUser;

  } catch (error) {
    // Enhanced error logging with context
    const errorContext = {
      userId: userId?.substring(0, 10) + "...", // Log partial ID for privacy
      email: email ? "***@" + email.split('@')[1] : "undefined", // Log domain only for privacy
      operation: "findOrCreateUser"
    };

    console.error("Database operation failed:", {
      error: error instanceof Error ? error.message : String(error),
      context: errorContext
    });

    // Re-throw with more specific error messages
    if (error instanceof Error) {
      if (error.message.includes("unique constraint")) {
        throw new Error("User with this email already exists");
      }
      if (error.message.includes("connection")) {
        throw new Error("Database connection failed");
      }
      throw error; // Re-throw original error if no specific handling needed
    }

    throw new Error("Unknown error occurred during user operation");
  }
};

type CreateCheckParams = {
  checkId: string;
  userId: string;
  textId: string;
};

export const createCheck = async ({
  checkId,
  userId,
  textId,
}: CreateCheckParams) => {
  const [newCheck] = await db
    .insert(checks)
    .values({
      slug: checkId,
      userId: extractClerkId(userId),
      textId,
      status: "pending",
    })
    .returning();

  return newCheck;
};

export const updateCheckResult = async (
  checkId: string,
  result: unknown
): Promise<void> => {
  await db
    .update(checks)
    .set({
      result,
      status: "completed",
      completedAt: new Date(),
    })
    .where(eq(checks.slug, checkId));
};

export const updateCheckStatus = async (
  checkId: string,
  status: "completed" | "failed" | "no_claims"
): Promise<void> => {
  await db
    .update(checks)
    .set({
      status,
      completedAt: new Date(),
    })
    .where(eq(checks.slug, checkId));
};
