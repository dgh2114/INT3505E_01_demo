import express from 'express';
import dotenv from 'dotenv';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import { v4 as uuidv4 } from 'uuid';

dotenv.config();


const app = express();
app.use(express.json());


// ===== In-memory stores (demo) =====
const users = [
// demo user (password: 123456)
// Mẹo: thay bằng DB thực tế
];

// Pre-seed one demo user
(async () => {
const hash = await bcrypt.hash('123456', 10);
users.push({ id: 'u1', email: 'admin@example.com', passwordHash: hash, role: 'admin', scopes: ['users:read', 'users:write', 'docs:read'] });
})();


// refresh token store: jti -> { userId, expiresAt, revoked, rotationParentJti }
const refreshStore = new Map();


// ===== Helpers =====
const {
PORT = 3000,
ACCESS_TOKEN_SECRET,
REFRESH_TOKEN_SECRET,
TOKEN_ISS = 'demo.auth',
TOKEN_AUD = 'demo.api',
ACCESS_TOKEN_TTL = '15m',
REFRESH_TOKEN_TTL = '7d'
} = process.env;

function signAccessToken({ sub, role, scopes }) {
const jti = uuidv4(); // jti cho access token (minh hoạ)
return jwt.sign(
{ sub, role, scopes, jti },
ACCESS_TOKEN_SECRET,
{ issuer: TOKEN_ISS, audience: TOKEN_AUD, expiresIn: ACCESS_TOKEN_TTL }
);
}


function signRefreshToken({ sub }) {
const jti = uuidv4();
const token = jwt.sign(
{ sub, jti, typ: 'refresh' },
REFRESH_TOKEN_SECRET,
{ issuer: TOKEN_ISS, audience: TOKEN_AUD, expiresIn: REFRESH_TOKEN_TTL }
);
const now = Date.now();
const ttlMs = parseTtlMs(REFRESH_TOKEN_TTL);
refreshStore.set(jti, { userId: sub, expiresAt: now + ttlMs, revoked: false, rotationParentJti: null });
return { token, jti };
}

function rotateRefreshToken(oldJti, sub) {
// revoke old
const old = refreshStore.get(oldJti);
if (old) old.revoked = true;


const newJti = uuidv4();
const token = jwt.sign(
{ sub, jti: newJti, typ: 'refresh' },
REFRESH_TOKEN_SECRET,
{ issuer: TOKEN_ISS, audience: TOKEN_AUD, expiresIn: REFRESH_TOKEN_TTL }
);
const now = Date.now();
const ttlMs = parseTtlMs(REFRESH_TOKEN_TTL);
refreshStore.set(newJti, { userId: sub, expiresAt: now + ttlMs, revoked: false, rotationParentJti: oldJti });
return { token, jti: newJti };
}

function parseTtlMs(ttl) {
// very small parser: supports m, h, d
const m = ttl.match(/^(\d+)(m|h|d)$/);
if (!m) return 15 * 60 * 1000;
const n = parseInt(m[1], 10);
const unit = m[2];
if (unit === 'm') return n * 60 * 1000;
if (unit === 'h') return n * 60 * 60 * 1000;
if (unit === 'd') return n * 24 * 60 * 60 * 1000;
return 15 * 60 * 1000;
}


// === Security: block obvious token leakage ===
app.use((req, res, next) => {
const q = req.query;
const suspicion = ['token', 'access_token', 'id_token', 'refresh_token']
.some(k => typeof q[k] === 'string' && q[k].length > 0);
if (suspicion) {
return res.status(400).json({ error: 'Possible token leakage in URL query. Use Authorization header.' });
}
next();
});

// ===== Auth Middlewares =====
function authenticate(req, res, next) {
const auth = req.headers['authorization'];
if (!auth || !auth.startsWith('Bearer ')) {
return res.status(401).json({ error: 'Missing Bearer token' });
}
const token = auth.slice('Bearer '.length);
try {
const payload = jwt.verify(token, ACCESS_TOKEN_SECRET, { issuer: TOKEN_ISS, audience: TOKEN_AUD });
req.user = payload; // { sub, role, scopes, jti, iat, exp }
return next();
} catch (err) {
return res.status(401).json({ error: 'Invalid or expired token' });
}
}


function requireRole(role) {
return (req, res, next) => {
if (!req.user || req.user.role !== role) {
return res.status(403).json({ error: 'Forbidden: insufficient role' });
}
next();
};
}

function requireScopes(...need) {
return (req, res, next) => {
const have = (req.user?.scopes) || [];
const ok = need.every(s => have.includes(s));
if (!ok) return res.status(403).json({ error: 'Forbidden: missing scopes', need });
next();
};
}


// ===== Routes =====
app.get('/', (req, res) => {
res.json({ status: 'OK', docs: '/docs' });
});

app.get('/docs', (req, res) => {
res.json({
message: 'Demo endpoints',
endpoints: {
'POST /auth/register': { body: { email: 'string', password: 'string', role: 'admin|editor|viewer' } },
'POST /auth/login': { body: { email: 'string', password: 'string' } },
'POST /auth/refresh': { body: { refreshToken: 'string' } },
'POST /auth/logout': { body: { refreshToken: 'string' } },
'GET /profile': { auth: 'Bearer access_token' },
'GET /admin/users': { auth: 'Bearer', role: 'admin' },
'GET /docs/secure': { auth: 'Bearer', scopes: ['docs:read'] }
}
});
});

app.post('/auth/register', async (req, res) => {
const { email, password, role = 'viewer' } = req.body || {};
if (!email || !password) return res.status(400).json({ error: 'email & password required' });
if (users.find(u => u.email === email)) return res.status(409).json({ error: 'email already exists' });
const passwordHash = await bcrypt.hash(password, 10);
const scopesByRole = {
admin: ['users:read', 'users:write', 'docs:read'],
editor: ['docs:read'],
viewer: ['docs:read']
};
const scopes = scopesByRole[role] || [];
const user = { id: uuidv4(), email, passwordHash, role, scopes };
users.push(user);
res.status(201).json({ message: 'registered', user: { id: user.id, email, role, scopes } });
});

app.post('/auth/login', async (req, res) => {
const { email, password } = req.body || {};
const user = users.find(u => u.email === email);
if (!user) return res.status(401).json({ error: 'invalid credentials' });
const ok = await bcrypt.compare(password, user.passwordHash);
if (!ok) return res.status(401).json({ error: 'invalid credentials' });
const accessToken = signAccessToken({ sub: user.id, role: user.role, scopes: user.scopes });
const { token: refreshToken, jti } = signRefreshToken({ sub: user.id });
res.json({
token_type: 'Bearer',
access_token: accessToken,
refresh_token: refreshToken,
refresh_jti: jti,
expires_in: ACCESS_TOKEN_TTL,
scope: user.scopes.join(' '),
role: user.role
});
});

app.post('/auth/refresh', (req, res) => {
const { refreshToken } = req.body || {};
if (!refreshToken) return res.status(400).json({ error: 'refreshToken required' });
try {
const payload = jwt.verify(refreshToken, REFRESH_TOKEN_SECRET, { issuer: TOKEN_ISS, audience: TOKEN_AUD });
const entry = refreshStore.get(payload.jti);
if (!entry || entry.revoked || entry.userId !== payload.sub || Date.now() > entry.expiresAt) {
return res.status(401).json({ error: 'invalid or revoked refresh token' });
}
// rotate refresh token to mitigate replay
const rotated = rotateRefreshToken(payload.jti, payload.sub);


// issue new access
const user = users.find(u => u.id === payload.sub);
const accessToken = signAccessToken({ sub: user.id, role: user.role, scopes: user.scopes });
res.json({
token_type: 'Bearer',
access_token: accessToken,
refresh_token: rotated.token,
refresh_jti: rotated.jti,
expires_in: ACCESS_TOKEN_TTL,
scope: user.scopes.join(' '),
role: user.role
});
} catch (e) {
return res.status(401).json({ error: 'invalid or expired refresh token' });
}
});

app.post('/auth/logout', (req, res) => {
const { refreshToken } = req.body || {};
if (!refreshToken) return res.status(400).json({ error: 'refreshToken required' });
try {
const payload = jwt.verify(refreshToken, REFRESH_TOKEN_SECRET, { issuer: TOKEN_ISS, audience: TOKEN_AUD });
const entry = refreshStore.get(payload.jti);
if (entry) entry.revoked = true;
return res.json({ message: 'logged out (refresh token revoked)' });
} catch {
return res.status(400).json({ error: 'invalid refresh token' });
}
});


// Protected routes
app.get('/profile', authenticate, (req, res) => {
const user = users.find(u => u.id === req.user.sub);
res.json({ id: user.id, email: user.email, role: user.role, scopes: user.scopes });
});


app.get('/admin/users', authenticate, requireRole('admin'), (req, res) => {
res.json(users.map(u => ({ id: u.id, email: u.email, role: u.role, scopes: u.scopes })));
});


app.get('/docs/secure', authenticate, requireScopes('docs:read'), (req, res) => {
res.json({ ok: true, msg: 'You have docs:read scope' });
});

app.listen(PORT, () => {
console.log(`Server running on http://localhost:${PORT}`);
});