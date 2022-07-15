const WORKDIR = "/marsbots";

module.exports = {
  apps: [
    {
      name: "doomer",
      script: `${WORKDIR}/bot.py`,
      interpreter: "python",
      args: `${WORKDIR}/bots/doomer2/doomer.json --cog-path=bots.doomer2.doomer --dotenv-path=${WORKDIR}/bots/doomer2/.env`,
      watch: [`${WORKDIR}/bots/doomer`],
      watch_delay: 1000,
    },
  ],
};
