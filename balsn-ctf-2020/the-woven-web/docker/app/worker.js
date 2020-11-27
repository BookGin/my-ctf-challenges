#!/usr/bin/env node

const {Builder, Capabilities} = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');
const redis = require('redis');
const client = redis.createClient('/var/run/redis/redis-server.sock');

let options = new chrome.Options();
options.addArguments(['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage']);

const TIMEOUT_MS = 5000;

async function browse(url) {
  const driver = await new Builder().forBrowser('chrome').setChromeOptions(options).build();
  await driver.manage().setTimeouts({
    pageLoad: TIMEOUT_MS,
    script: TIMEOUT_MS
  })
  try {
    await driver.get(url);
    await new Promise(resolve => setTimeout(resolve, TIMEOUT_MS));
  } catch (e) {
    console.log(url, e);
  } finally {
    await driver.quit();
  }
}

function main() {
  client.blpop(['urls', 0], async (_, listNameAndUrl) => {
    let url = listNameAndUrl[1];
    console.log(url);
    await browse(url);
    console.log(url + " done");
    main();
  }); 
}

console.log("Start worker......");
main()
