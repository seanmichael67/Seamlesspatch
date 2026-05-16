const fs = require('fs/promises');
const crypto = require('crypto');
const formidable = require('formidable');
const { createClient } = require('@supabase/supabase-js');

const BUCKET = 'seamlesspatch-quote-photos';

module.exports.config = {
  api: {
    bodyParser: false,
  },
};

function first(value) {
  return Array.isArray(value) ? value[0] : value;
}

function cleanText(value) {
  return String(first(value) || '').trim();
}

function safeFileName(name) {
  return String(name || 'damage-photo.jpg')
    .toLowerCase()
    .replace(/[^a-z0-9._-]+/g, '-')
    .replace(/^-+|-+$/g, '') || 'damage-photo.jpg';
}

function parseForm(req) {
  const form = formidable({
    multiples: true,
    maxFileSize: 10 * 1024 * 1024,
    maxTotalFileSize: 35 * 1024 * 1024,
    filter(part) {
      if (part.name !== 'photos') return true;
      return !part.mimetype || part.mimetype.startsWith('image/');
    },
  });

  return new Promise((resolve, reject) => {
    form.parse(req, (err, fields, files) => {
      if (err) reject(err);
      else resolve({ fields, files });
    });
  });
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false, error: 'Method not allowed' });
  }

  const supabaseUrl = process.env.SUPABASE_URL;
  const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!supabaseUrl || !serviceRoleKey) {
    return res.status(500).json({ ok: false, error: 'Quote backend is not configured yet' });
  }

  try {
    const { fields, files } = await parseForm(req);
    const name = cleanText(fields.name);
    const phone = cleanText(fields.phone);
    const email = cleanText(fields.email);
    const zip = cleanText(fields.zip);
    const damage = cleanText(fields.damage);
    const pageUrl = cleanText(fields.page_url);
    const userAgent = cleanText(fields.user_agent || req.headers['user-agent']);

    if (!name || !phone || !email || !zip) {
      return res.status(400).json({ ok: false, error: 'Name, phone, email, and ZIP are required' });
    }

    const quoteId = crypto.randomUUID();
    const supabase = createClient(supabaseUrl, serviceRoleKey, {
      auth: { persistSession: false, autoRefreshToken: false },
    });

    const uploadedPaths = [];
    const rawPhotos = files.photos ? (Array.isArray(files.photos) ? files.photos : [files.photos]) : [];

    for (let i = 0; i < rawPhotos.length; i += 1) {
      const file = rawPhotos[i];
      if (!file || !file.filepath || file.size === 0) continue;
      const body = await fs.readFile(file.filepath);
      const objectPath = `quote-uploads/${quoteId}/${Date.now()}-${i + 1}-${safeFileName(file.originalFilename)}`;
      const { error: uploadError } = await supabase.storage
        .from(BUCKET)
        .upload(objectPath, body, {
          contentType: file.mimetype || 'application/octet-stream',
          cacheControl: '3600',
          upsert: false,
        });
      if (uploadError) throw uploadError;
      uploadedPaths.push(objectPath);
    }

    const { error: insertError } = await supabase
      .from('seamlesspatch_quote_requests')
      .insert({
        id: quoteId,
        source: 'seamlesspatch.com',
        name,
        phone,
        email,
        zip,
        damage_description: damage,
        photo_paths: uploadedPaths,
        user_agent: userAgent,
        page_url: pageUrl,
      });

    if (insertError) throw insertError;

    return res.status(200).json({ ok: true, id: quoteId, photo_count: uploadedPaths.length });
  } catch (error) {
    console.error('quote intake error', error);
    return res.status(500).json({ ok: false, error: 'Unable to save quote request' });
  }
};
