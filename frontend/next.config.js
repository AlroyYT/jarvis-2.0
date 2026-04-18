/** @type {import('next').NextConfig} */
const nextConfig = {
  // Disable StrictMode — it double-invokes effects in dev which kills
  // the Web Speech API recognition loop (Chrome only allows one instance)
  reactStrictMode: false,
}

module.exports = nextConfig