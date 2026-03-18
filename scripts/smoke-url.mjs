const appUrl = process.env.PUBLIC_APP_URL;
const apiUrl = process.env.PUBLIC_API_URL;

if (!appUrl || !apiUrl) {
  console.error("PUBLIC_APP_URL and PUBLIC_API_URL must be set.");
  process.exit(1);
}

async function expectOk(url, label) {
  const response = await fetch(url, { redirect: "follow" });
  if (!response.ok) {
    throw new Error(`${label} failed with status ${response.status}`);
  }
  return response;
}

async function main() {
  await expectOk(appUrl, "Public app root");

  const health = await expectOk(`${apiUrl}/health`, "API health");
  const healthBody = await health.json();
  if (healthBody.status !== "ok") {
    throw new Error("API health payload is invalid.");
  }

  const readiness = await expectOk(`${apiUrl}/readiness`, "API readiness");
  const readinessBody = await readiness.json();
  if (!["ready", "degraded"].includes(readinessBody.status)) {
    throw new Error("API readiness payload is invalid.");
  }

  const incidents = await expectOk(`${apiUrl}/v1/incidents`, "API incidents");
  const incidentsBody = await incidents.json();
  if (!Array.isArray(incidentsBody.incidents) || incidentsBody.incidents.length === 0) {
    throw new Error("API incidents payload is empty or invalid.");
  }

  console.log("Public URL smoke checks passed.");
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});
