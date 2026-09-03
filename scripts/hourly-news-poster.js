import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI();

async function runHourlyNewsPipeline() {
  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: 'Write a short, punchy hourly news update covering remote careers, Facebook content distribution, and web dev AI tools.',
    });

    const newsPost = response.text;
    console.log("Generated Hourly Update:\n", newsPost);

    // If you configure a webhook URL secret later, this will push it automatically
    if (process.env.PUBLISH_WEBHOOK_URL) {
      await publishToWebhook(newsPost);
    }
  } catch (error) {
    console.error("Error generating hourly news:", error);
    process.exit(1);
  }
}

async function publishToWebhook(content) {
  const fetch = (await import('node-fetch')).default;
  await fetch(process.env.PUBLISH_WEBHOOK_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: content })
  });
}

runHourlyNewsPipeline();
