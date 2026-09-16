#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const source = path.resolve(ROOT, process.argv[2] || "private/trip-data.json");
const destination = path.resolve(ROOT, process.argv[3] || "trip-data.json");
const password = process.env.TRAVEL_PAGE_PASSWORD;
const iterations = 600000;

if (!password) throw new Error("TRAVEL_PAGE_PASSWORD is required");

const plaintext = await fs.readFile(source);
JSON.parse(plaintext.toString("utf8"));
const salt = crypto.randomBytes(16);
const iv = crypto.randomBytes(12);
const key = crypto.pbkdf2Sync(password, salt, iterations, 32, "sha256");
const cipher = crypto.createCipheriv("aes-256-gcm", key, iv);
const encrypted = Buffer.concat([cipher.update(plaintext), cipher.final()]);
const ciphertext = Buffer.concat([encrypted, cipher.getAuthTag()]);
const envelope = {
  version: 1,
  algorithm: "AES-GCM",
  kdf: "PBKDF2-SHA-256",
  iterations,
  salt: salt.toString("base64"),
  iv: iv.toString("base64"),
  ciphertext: ciphertext.toString("base64")
};

await fs.writeFile(destination, `${JSON.stringify(envelope)}\n`, { mode: 0o600 });
console.log(`Encrypted ${path.relative(ROOT, source)} -> ${path.relative(ROOT, destination)}`);
