const test = require('node:test');
const assert = require('node:assert/strict');

function calculateStress(baseDscr, revenueDecline) {
  return Math.max(0.65, baseDscr - revenueDecline * 0.02);
}

test('a ten percent contraction retains covenant headroom', () => {
  assert.equal(calculateStress(1.62, 10).toFixed(2), '1.42');
});

test('severe stress does not report a negative DSCR', () => {
  assert.equal(calculateStress(1.62, 100), 0.65);
});
