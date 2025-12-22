// Background worker
chrome.storage.onChanged.addListener((changes, area) => {
  if (area !== "sync") return;
  console.log("Updated credentials:", changes);
});