import type { NextConfig } from 'next'

const config: NextConfig = {
  webpack: (config) => {
    config.resolve.alias.canvas = false;
    return config;
  },
  transpilePackages: [
    '@react-pdf-viewer/core',
    '@react-pdf-viewer/default-layout'
  ]
}

export default config;