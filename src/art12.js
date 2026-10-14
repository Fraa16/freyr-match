
/* ===================== round 3 art: gift boxes, cucumbers, alarm clocks, the magic feather, triple boxes ===================== */
// a present: blue paper, pink ribbon, a big bow, white dots
const GIFT_SVG = `<svg viewBox="0 0 100 100"><g ${OL('#1B4C9C')}>` +
  `<rect x="15" y="45" width="70" height="46" rx="8" fill="url(#gBlue)"/><rect x="10" y="32" width="80" height="18" rx="6.5" fill="url(#gBlue)"/></g>` +
  `<g fill="#fff" opacity=".6"><circle cx="25" cy="62" r="3.4"/><circle cx="74" cy="60" r="3.2"/><circle cx="30" cy="81" r="2.8"/><circle cx="70" cy="80" r="3.4"/><circle cx="22" cy="40" r="2.4"/><circle cx="79" cy="41" r="2.4"/></g>` +
  `<rect x="43.5" y="32.6" width="13" height="57.8" fill="url(#gPink)" stroke="#9E0C57" stroke-width="2.2"/>` +
  `<path d="M16 50 H84" stroke="#1B4C9C" stroke-width="2.4" opacity=".45"/>` +
  `<g fill="url(#gPink)" ${OL('#9E0C57')}><path d="M50 32 Q31 9 21 19 Q14 31 50 32Z"/><path d="M50 32 Q69 9 79 19 Q86 31 50 32Z"/><circle cx="50" cy="30.5" r="6.5"/></g>` +
  `<path d="M26 20 Q32 15 39 20 M74 20 Q68 15 61 20" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" opacity=".85"/>` +
  `${SHINE(27, 39, 9, 2.6, -4)}${SHINE(25, 55, 5, 2.2, -12)}</svg>`;
// the cucumber: cats are terrified of them, this one knows it
const CUKE_SVG = `<svg viewBox="0 0 100 100"><g transform="translate(50 52) rotate(-36) scale(1.1) translate(-50 -52)">` +
  `<rect x="8" y="35" width="84" height="33" rx="16.5" fill="url(#gGreen)" stroke="#155F20" stroke-width="2.8"/>` +
  `<path d="M20 41 Q50 36.5 82 42 M18 61 Q50 65.5 84 60" fill="none" stroke="#2C9431" stroke-width="2.6" stroke-linecap="round" opacity=".55"/>` +
  `<g fill="#DFFFCB"><circle cx="21" cy="50" r="1.9"/><circle cx="31" cy="44" r="1.7"/><circle cx="33" cy="58" r="1.9"/><circle cx="72" cy="44" r="1.7"/><circle cx="76" cy="58" r="1.9"/><circle cx="83" cy="50" r="1.6"/></g>` +
  `<ellipse cx="89.5" cy="51.5" rx="3.6" ry="11" fill="#A8EC86" stroke="#155F20" stroke-width="2"/>` +
  `<path d="M8.5 51 q-6 -2 -6 -9" fill="none" stroke="#155F20" stroke-width="3.2" stroke-linecap="round"/>` +
  `<g stroke="#155F20" stroke-width="1.8"><circle cx="45" cy="47" r="6.4" fill="#fff"/><circle cx="60" cy="47" r="6.4" fill="#fff"/></g>` +
  `<circle cx="46.6" cy="48.6" r="3" fill="#1A1430"/><circle cx="61.6" cy="48.6" r="3" fill="#1A1430"/><circle cx="45.4" cy="47.2" r="1.1" fill="#fff"/><circle cx="60.4" cy="47.2" r="1.1" fill="#fff"/>` +
  `<path d="M47 58 Q53 62.5 60 57" fill="none" stroke="#155F20" stroke-width="2.6" stroke-linecap="round"/>` +
  `<path d="M22 40 Q38 37 52 38" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round" opacity=".7"/></g></svg>`;
// cardboard boxes: one tape per layer, the third layer is a gold strap
const BOX3_SVG = hp => `<svg viewBox="0 0 100 100"><g ${OL('#7E4A1C')}><path d="M10 34 L3 20 L45 20 L50 34Z" fill="#F7DFB6"/><path d="M90 34 L97 20 L55 20 L50 34Z" fill="#F7DFB6"/><rect x="10" y="34" width="80" height="58" rx="8" fill="url(#gCard)"/></g>` +
  (hp > 2 ? `<rect x="21" y="35.4" width="8" height="55.2" fill="url(#gGold)"/><rect x="71" y="35.4" width="8" height="55.2" fill="url(#gGold)"/>` : '') +
  `<rect x="44" y="35.4" width="12" height="55.2" fill="url(#gPink)"/>` + (hp > 1 ? `<rect x="11.4" y="56" width="77.2" height="11" fill="url(#gPink)"/>` : '') +
  (hp > 2 ? `<path transform="translate(39.6 51.4) scale(.86)" d="${HEART}" fill="url(#gHeart)" stroke="#fff" stroke-width="1.6"/>` : '') +
  `<path d="M16 42 Q28 38 38 40" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" opacity=".75"/>` +
  `<path d="M47 37 V88" stroke="#fff" stroke-width="2" opacity=".55"/></svg>`;
// the alarm clock badge that sits on a treat, and a big one for cards and goals
const CLOCK_BADGE = `<svg viewBox="0 0 40 40" aria-hidden="true"><g stroke="#6E0016" stroke-width="2.2" stroke-linejoin="round">` +
  `<path d="M6.5 13 Q4 4.5 12.5 4.5 Q15.5 5.5 14.5 9Z" fill="url(#gRed)"/><path d="M33.5 13 Q36 4.5 27.5 4.5 Q24.5 5.5 25.5 9Z" fill="url(#gRed)"/>` +
  `<path d="M10.5 33 L7 37.5 M29.5 33 L33 37.5" stroke-linecap="round"/><circle cx="20" cy="22.5" r="14.2" fill="url(#gRed)"/><circle cx="20" cy="22.5" r="10.6" fill="#fff" stroke-width="1.4"/></g></svg>`;
const CLOCK_ICON = `<svg viewBox="0 0 100 100"><g stroke="#6E0016" stroke-width="3.4" stroke-linejoin="round" stroke-linecap="round">` +
  `<path d="M17 33 Q11 11 32 11 Q39 13 37 22Z" fill="url(#gRed)"/><path d="M83 33 Q89 11 68 11 Q61 13 63 22Z" fill="url(#gRed)"/>` +
  `<path d="M27 82 L19 93 M73 82 L81 93"/><circle cx="50" cy="56" r="35" fill="url(#gRed)"/><circle cx="50" cy="56" r="26" fill="#fff" stroke-width="2.4"/>` +
  `<path d="M50 56 V38 M50 56 L62 63" stroke="#2A1640" stroke-width="5"/><circle cx="50" cy="56" r="3.6" fill="#2A1640" stroke="none"/></g>` +
  `<g fill="#2A1640"><circle cx="50" cy="34.5" r="2"/><circle cx="71.5" cy="56" r="2"/><circle cx="50" cy="77.5" r="2"/><circle cx="28.5" cy="56" r="2"/></g>` +
  `<path d="M29 41 Q34 30 46 28" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".7"/></svg>`;
// the magic feather: a pink plume on a golden grip, with sparkles
const FEATHER_TOOL = `<svg viewBox="0 0 100 100"><g transform="rotate(32 50 52)">` +
  `<path d="M50 5 Q74 28 63 63 Q57 75 50 79 Q43 75 37 63 Q26 28 50 5Z" fill="url(#gPink)" stroke="#9E0C57" stroke-width="2.6" stroke-linejoin="round"/>` +
  `<path d="M50 20 L41 13 M50 31 L37 23 M50 42 L36 34 M50 53 L38 47 M50 31 L63 23 M50 42 L64 34 M50 53 L62 47 M50 20 L59 13" stroke="#FFC6E0" stroke-width="2.2" stroke-linecap="round"/>` +
  `<path d="M50 12 V84" stroke="#fff" stroke-width="3.2" stroke-linecap="round"/>` +
  `<rect x="45.5" y="76" width="9" height="19" rx="4" fill="url(#gGold)" stroke="#9A5200" stroke-width="2.4"/></g>` +
  `<g fill="url(#gGold)" stroke="#9A5200" stroke-width="1.6" stroke-linejoin="round"><path d="M80 9 l3.6 8 8 3.6 -8 3.6 -3.6 8 -3.6 -8 -8 -3.6 8 -3.6Z"/><path d="M17 64 l2.4 5.2 5.2 2.4 -5.2 2.4 -2.4 5.2 -2.4 -5.2 -5.2 -2.4 5.2 -2.4Z"/></g></svg>`;
// gold rush goal: a golden coin with a paw
const GOLDPAW_SVG = `<svg viewBox="0 0 100 100"><circle cx="50" cy="52" r="38" fill="url(#gGold)" ${OL('#9A5200')}/><circle cx="50" cy="52" r="29" fill="none" stroke="#FFF3B0" stroke-width="3" opacity=".8"/>` +
  `<g fill="#B86B00"><ellipse cx="50" cy="61" rx="12" ry="10"/><ellipse cx="35" cy="48" rx="5" ry="6.4"/><ellipse cx="45" cy="39" rx="5" ry="6.4"/><ellipse cx="55" cy="39" rx="5" ry="6.4"/><ellipse cx="65" cy="48" rx="5" ry="6.4"/></g>` +
  `${SHINE(36, 30, 11, 4)}</svg>`;
// the turbo robot: a lightning bolt badge
const BOLT_SVG = `<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M23 2 L8 22 H18 L14 38 L32 15 H21Z" fill="url(#gGold)" stroke="#8A4A00" stroke-width="2.4" stroke-linejoin="round"/></svg>`;
const VAC_TURBO_ICON = `<span class="lico two turbo"><span class="ico">${VAC_ICON}</span><span class="ico">${BOLT_SVG}</span></span>`;
