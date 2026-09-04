/* HyperFrames 0.6.69: one paused GSAP timeline, registered as data-composition-id. */
window.__timelines = window.__timelines || {};

const tl = gsap.timeline({ paused: true });

// Cover is visible at t=0 — do not fade it in from opacity 0.
tl.to("#card-cover", { opacity: 0, duration: 0.25, ease: "none" }, 1.75);

const cards = [
  ["#card-rank-05", 2.0, 6.0],
  ["#card-rank-04", 6.0, 10.0],
  ["#card-rank-03", 10.0, 14.0],
  ["#card-rank-02", 14.0, 18.0],
  ["#card-rank-01", 18.0, 22.0],
  ["#card-outro", 22.0, 26.0],
  ["#card-cta", 26.0, 30.0],
];

for (const [selector, start, end] of cards) {
  tl.fromTo(
    selector,
    { opacity: 0 },
    { opacity: 1, duration: 0.3, ease: "none" },
    start,
  );
  tl.to(selector, { opacity: 0, duration: 0.25, ease: "none" }, end - 0.25);
}

window.__timelines["main"] = tl;
