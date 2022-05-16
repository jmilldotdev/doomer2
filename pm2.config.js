module.exports = {
  apps: [
    {
      name: "doomer",
      script: "../../bot.py",
      interpreter: "python",
      args: "./doomer.json --cog-path=bots.doomer2.doomer --dotenv-path=.env",
      watch: ["."],
      ignore_watch: ["__pycache__", "*.pyc", "./doomer_settings.json"],
      watch_delay: 1000,
    },
  ],
};
