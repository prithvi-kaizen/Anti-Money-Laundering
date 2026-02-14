/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    // Only proxy API calls in development — Vercel handles routing in production
    if (process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/api/:path*',
          destination: 'http://localhost:8000/:path*',
        },
      ];
    }
    return [];
  },
};

module.exports = nextConfig;
