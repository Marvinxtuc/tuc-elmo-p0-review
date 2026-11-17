import { CREDENTIAL_ENV_NAMES } from "@workspace/config/env-registry";
import { isP0Offline } from "../constants";
import { db } from "../db/db";
import { secrets } from "../db/schema";
import {
	decryptSecret,
	ENCRYPTION_KEY_ENV,
	type EncryptedPayload,
	EncryptionKeyError,
	encryptSecret,
	getKeyring,
	type Keyring,
	UnknownKeyError,
} from "./crypto";

// Providers read every credential through getCredential: a stored override if
// one exists, otherwise process.env. The overlay of stored overrides is rebuilt
// on an interval by refreshCredentialOverlay (see ./refresh).
const overlay = new Map<string, string>();
const unreadable = new Set<string>();

/** Stored override if present, else process.env. Sync so `isConfigured()` stays sync. */
export function getCredential(name: string): string | undefined {
	if (isP0Offline() && unreadable.has(name)) throw new Error("P0 stored credential is unreadable");
	return overlay.get(name) ?? process.env[name];
}

/** The environment with stored overrides applied, so a startup check counts a
 *  credential saved in the database the same as one set in .env. */
export function withStoredCredentials(
	env: Record<string, string | undefined> = process.env,
): Record<string, string | undefined> {
	const result = { ...env, ...Object.fromEntries(overlay) };
	if (isP0Offline()) {
		for (const name of unreadable) result[name] = undefined;
	}
	return result;
}

export function clearCredentialOverlay(): void {
	overlay.clear();
	unreadable.clear();
}

/** AAD binds each ciphertext to the env var it stands in for, so a payload can't
 *  be replayed under a different name even by someone with DB write access. */
function aadForName(name: string): string {
	return `secret:${name}`;
}

function maskCredentialFallback(): void {
	overlay.clear();
	for (const name of CREDENTIAL_ENV_NAMES) unreadable.add(name);
}

function credentialReadFailed(error: unknown): never {
	if (isP0Offline()) maskCredentialFallback();
	throw error;
}

export async function refreshCredentialOverlay(): Promise<void> {
	let keyring: Keyring | null = null;
	try {
		keyring = getKeyring();
	} catch (e) {
		if (!(e instanceof EncryptionKeyError)) throw e;
		console.error(`[secrets] ${e.message} — every stored credential is unreadable until this is corrected`);
	}
	// No key means nothing can be stored, so there is no query to make.
	if (!keyring) {
		unreadable.clear();
		maskCredentialFallback();
		return;
	}

	const rows = await db
		.select({ name: secrets.name, encryptedValue: secrets.encryptedValue })
		.from(secrets)
		.catch(credentialReadFailed);

	const next = new Map<string, string>();
	const nextUnreadable = new Set<string>();
	for (const row of rows) {
		if (!CREDENTIAL_ENV_NAMES.has(row.name)) continue;
		try {
			next.set(row.name, await decryptSecret(row.encryptedValue, { keyring, aad: aadForName(row.name) }));
		} catch (e) {
			nextUnreadable.add(row.name);
			console.error(
				e instanceof UnknownKeyError
					? `[secrets] stored secret "${row.name}" is ${e.message} — restore that key there to finish the rotation`
					: `[secrets] stored secret "${row.name}" will not decrypt under the key it names — it may be corrupt or tampered with`,
			);
		}
	}

	overlay.clear();
	unreadable.clear();
	for (const name of nextUnreadable) unreadable.add(name);
	for (const [name, value] of next) overlay.set(name, value);
}

/** Encrypt one credential for the write path. Throws when the name is not an
 *  overridable credential, or when no encryption key is set. */
export async function encryptCredential(name: string, value: string): Promise<EncryptedPayload> {
	if (!CREDENTIAL_ENV_NAMES.has(name)) {
		throw new Error(`"${name}" is not an overridable credential`);
	}
	const keyring = getKeyring();
	if (!keyring) {
		throw new EncryptionKeyError(`${ENCRYPTION_KEY_ENV} is not set — cannot store encrypted credentials`);
	}
	return encryptSecret(value, { key: keyring.primary, aad: aadForName(name) });
}
