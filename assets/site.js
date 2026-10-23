// Optional enhancement; navigation, downloads, and FAQs also work without JavaScript.
const year = document.getElementById('year');
if (year) year.textContent = String(new Date().getFullYear());
