#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const file = path.join(ROOT, "trip-data.json");
const requiredKeys = ["version", "algorithm", "kdf", "iterations", "salt", "iv", "ciphertext"];

let envelope;
try {
  envelope = JSON.parse(await fs.readFile(file, "utf8"));
} catch (error) {
  throw new Error(`trip-data.json must be a valid encrypted JSON envelope: ${error.message}`);
}

if (!envelope || typeof envelope !== "object" || Array.isArray(envelope)) throw new Error("trip-data.json encrypted envelope is invalid");
if (Object.keys(envelope).some((key) => !requiredKeys.includes(key))) throw new Error("trip-data.json encrypted envelope contains unexpected fields");
if (requiredKeys.some((key) => !Object.hasOwn(envelope, key))) throw new Error("trip-data.json encrypted envelope is incomplete");
if (envelope.version !== 1 || envelope.algorithm !== "AES-GCM" || envelope.kdf !== "PBKDF2-SHA-256") throw new Error("trip-data.json encryption metadata is unsupported");
if (!Number.isInteger(envelope.iterations) || envelope.iterations < 600000) throw new Error("trip-data.json PBKDF2 work factor is too low");

for (const [key, expectedLength] of [["salt", 16], ["iv", 12]]) {
  const value = Buffer.from(envelope[key], "base64");
  if (value.length !== expectedLength || value.toString("base64") !== envelope[key]) throw new Error(`trip-data.json ${key} is invalid`);
}

const ciphertext = Buffer.from(envelope.ciphertext, "base64");
if (ciphertext.length < 32 || ciphertext.toString("base64") !== envelope.ciphertext) throw new Error("trip-data.json ciphertext is invalid");
if (/Sydney|悉尼|CZ3152|flightJourneys|primaryDestinationCountries/.test(await fs.readFile(file, "utf8"))) {
  throw new Error("trip-data.json appears to expose plaintext travel data");
}

console.log("validate-encrypted-trip: PASS");
