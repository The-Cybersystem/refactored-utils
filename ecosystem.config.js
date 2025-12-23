module.exports = {
    apps: [{
    name: '',  // Custom name for your bot
    script: 'main.py',     // Path to your main Python script
         interpreter: '',  // Full path to your custom Python interpreter
         cwd: '',  // Absolute path to the bot's working directory
         env: {
           NODE_ENV: 'development'
         },
         instances: 1,  // Run one instance (bots usually don't need clustering)
         autorestart: true,  // Auto-restart on crashes
         watch: false  // Set to true if you want PM2 to restart on file changes (optional)
       }]
     };