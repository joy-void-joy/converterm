import { defineConfig, loadEnv } from 'vite'

export default ({ mode }) => {
  process.env = { ...process.env, ...loadEnv(mode, process.cwd()) }

  return defineConfig({
    server: {
      port: Number(process.env.VITE_FRONTEND_PORT),
      watch: {
        ignored: [
          '!../backend/**',
          '../backend/node_modules/**',
          '../backend/__pycache__/**',
        ],
      },
    },
  })
}
