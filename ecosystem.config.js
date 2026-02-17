module.exports = {
    apps: [{
        name: 'whisper-transcription-api',
        script: 'api.py',
        interpreter: 'python',
        instances: 1,
        autorestart: true,
        watch: false,
        max_memory_restart: '5G',
        env: {
            NODE_ENV: 'development'
        },
        env_production: {
            NODE_ENV: 'production'
        }
    }]
}