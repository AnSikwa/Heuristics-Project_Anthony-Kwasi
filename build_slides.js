// Final presentation slide deck for CS 57200 Heuristic Problem Solving
// Anthony Kwasi - Track B: Search & Optimization
// 15-minute presentation, 13 slides

const pptxgen = require('pptxgenjs');
const fs = require('fs');
const path = require('path');

const deck = new pptxgen();
deck.layout = 'LAYOUT_16x9'; // 10" x 5.625"
deck.title = 'CS57200 Final Presentation - Heuristic A* Search';
deck.author = 'Anthony Kwasi';

// ---- Design tokens ----
const COLORS = {
  bg: 'F7F6F2',          // warm off-white
  bgDark: '0E2A2C',      // deep teal for title/conclusion slides
  text: '28251D',        // primary text
  textMuted: '7A7974',   // secondary
  textOnDark: 'F0EDE5',  // text on dark
  textMutedOnDark: 'A9C4C8',
  accent: '01696F',      // hydra teal
  accentLight: '4F98A3',
  border: 'D4D1CA',
  card: 'FBFBF9',
  // chart palette
  manhattan: 'A84B2F',
  linearConflict: '20808D',
  pdb: '1B474D',
};

const F = {
  heading: 'Trebuchet MS',
  body: 'Calibri',
};

// ---- Helpers ----
function addFooter(sl, page, total) {
  sl.addText(`${page} / ${total}`, {
    x: 8.8, y: 5.25, w: 1.0, h: 0.3,
    fontSize: 10, fontFace: F.body, color: COLORS.textMuted,
    align: 'right', margin: 0,
  });
  sl.addText('Anthony Kwasi  |  CS 57200  |  Spring 2026', {
    x: 0.5, y: 5.25, w: 6, h: 0.3,
    fontSize: 10, fontFace: F.body, color: COLORS.textMuted,
    align: 'left', margin: 0,
  });
}

function addTitleBar(sl, title) {
  sl.addText(title, {
    x: 0.5, y: 0.35, w: 9, h: 0.7,
    fontSize: 28, fontFace: F.heading, bold: true,
    color: COLORS.text, margin: 0, align: 'left',
  });
  // thin teal underline accent? skip per design rules
}

const TOTAL = 13;

// =================== Slide 1 - Title ===================
{
  const sl = deck.addSlide();
  sl.background = { color: COLORS.bgDark };

  sl.addText('Heuristic A* Search', {
    x: 0.6, y: 1.3, w: 8.8, h: 0.9,
    fontSize: 48, fontFace: F.heading, bold: true,
    color: COLORS.textOnDark, margin: 0, align: 'left',
  });
  sl.addText('for Large Sliding Puzzles', {
    x: 0.6, y: 2.15, w: 8.8, h: 0.7,
    fontSize: 36, fontFace: F.heading,
    color: COLORS.textOnDark, margin: 0, align: 'left',
  });
  sl.addText('Manhattan vs Linear Conflict vs Disjoint Pattern Databases', {
    x: 0.6, y: 2.95, w: 8.8, h: 0.5,
    fontSize: 18, fontFace: F.body, italic: true,
    color: COLORS.textMutedOnDark, margin: 0, align: 'left',
  });

  // separator block
  sl.addShape(deck.shapes.RECTANGLE, {
    x: 0.6, y: 3.7, w: 0.6, h: 0.05, fill: { color: COLORS.accentLight }, line: { color: COLORS.accentLight },
  });

  sl.addText('Anthony Kwasi', {
    x: 0.6, y: 3.9, w: 8.8, h: 0.4,
    fontSize: 22, fontFace: F.body, bold: true, color: COLORS.textOnDark, margin: 0,
  });
  sl.addText('CS 57200 - Heuristic Problem Solving  |  Track B: Search & Optimization', {
    x: 0.6, y: 4.3, w: 8.8, h: 0.35,
    fontSize: 14, fontFace: F.body, color: COLORS.textMutedOnDark, margin: 0,
  });
  sl.addText('Purdue University - Spring 2026', {
    x: 0.6, y: 4.65, w: 8.8, h: 0.35,
    fontSize: 14, fontFace: F.body, color: COLORS.textMutedOnDark, margin: 0,
  });
}

// =================== Slide 2 - Agenda ===================
{
  const sl = deck.addSlide();
  sl.background = { color: COLORS.bg };
  addTitleBar(sl, 'Agenda');

  const items = [
    ['1', 'Problem & motivation', 'Why the 15-puzzle still matters'],
    ['2', 'Background', 'A*, IDA*, admissible heuristics'],
    ['3', 'System design', 'Pluggable heuristic architecture'],
    ['4', 'Three heuristics', 'Manhattan, Linear Conflict, Disjoint PDB'],
    ['5', 'Experimental setup', 'Ablation methodology and seeds'],
    ['6', 'Headline result', '15.2x speedup at depth 50'],
    ['7', 'Analysis & limitations', 'Why PDB wins; what is left'],
    ['8', 'Future work & demo', 'Where to go next'],
  ];

  const startY = 1.4;
  const rowH = 0.42;
  items.forEach(([num, title, sub], i) => {
    const y = startY + i * rowH;
    sl.addText(num, {
      x: 0.7, y, w: 0.5, h: rowH,
      fontSize: 20, fontFace: F.heading, bold: true,
      color: COLORS.accent, margin: 0, align: 'left',
    });
    sl.addText(title, {
      x: 1.3, y, w: 3.7, h: rowH,
      fontSize: 16, fontFace: F.body, bold: true,
      color: COLORS.text, margin: 0, align: 'left',
    });
    sl.addText(sub, {
      x: 5.0, y, w: 4.4, h: rowH,
      fontSize: 14, fontFace: F.body,
      color: COLORS.textMuted, margin: 0, align: 'left',
    });
  });

  addFooter(sl, 2, TOTAL);
}

// =================== Slide 3 - Problem & motivation ===================
{
  const sl = deck.addSlide();
  sl.background = { color: COLORS.bg };
  addTitleBar(sl, 'The 15-puzzle: a canonical hard search problem');

  // Left column: stat callouts
  const stats = [
    ['~10\u00B9\u00B3', 'reachable states on 4x4'],
    ['~80', 'maximum optimal depth'],
    ['~2.13', 'average branching factor'],
  ];
  stats.forEach(([big, label], i) => {
    const y = 1.4 + i * 1.15;
    sl.addText(big, {
      x: 0.5, y, w: 4.2, h: 0.7,
      fontSize: 56, fontFace: F.heading, bold: true,
      color: COLORS.accent, margin: 0, align: 'left',
    });
    sl.addText(label, {
      x: 0.5, y: y + 0.7, w: 4.2, h: 0.3,
      fontSize: 13, fontFace: F.body,
      color: COLORS.textMuted, margin: 0, align: 'left',
    });
  });

  // Right column: why it matters
  sl.addText('Why it matters', {
    x: 5.2, y: 1.4, w: 4.3, h: 0.4,
    fontSize: 18, fontFace: F.heading, bold: true,
    color: COLORS.text, margin: 0,
  });
  const points = [
    'Brute-force BFS exhausts memory on 4x4.',
    'Optimality requires admissible heuristics.',
    'Direct analogue for warehouse routing, robot path planning, and game AI.',
    'Benchmark for evaluating heuristic quality on the same instances.',
  ];
  sl.addText(
    points.map((p, i) => ({
      text: p,
      options: { breakLine: i < points.length - 1, bullet: { code: '2022' } },
    })),
    {
      x: 5.2, y: 1.85, w: 4.3, h: 3.2,
      fontSize: 14, fontFace: F.body, color: COLORS.text,
      paraSpaceAfter: 8, margin: 0, valign: 'top',
    },
  );

  addFooter(sl, 3, TOTAL);
}

// =================== Slide 4 - Background ===================
{
  const sl = deck.addSlide();
  sl.background = { color: COLORS.bg };
  addTitleBar(sl, 'Background: A*, IDA*, and admissibility');

  // 2x2 grid of cards
  const cards = [
    { title: 'A* search',
      body: 'Best-first with f(n)=g(n)+h(n). Admissible h yields optimal solutions; consistent h avoids re-expansion.',
      ref: 'Hart, Nilsson & Raphael (1968)' },
    { title: 'IDA*',
      body: 'Iterative-deepening DFS bounded by f-threshold. Memory O(d) - the only practical option at depth 80.',
      ref: 'Korf (1985)' },
    { title: 'Admissibility',
      body: 'h(n) <= true cost from n. Required for optimality. Empirically signals as identical solution depths across heuristics.',
      ref: 'Russell & Norvig (2021)' },
    { title: 'Heuristic quality',
      body: 'Closer h is to true cost, fewer nodes A* expands. Stronger heuristics trade compute for fewer expansions.',
      ref: 'Pearl (1984)' },
  ];

  const cardW = 4.2, cardH = 1.7;
  cards.forEach((c, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.5 + col * 4.55;
    const y = 1.4 + row * 1.95;
    sl.addShape(deck.shapes.RECTANGLE, {
      x, y, w: cardW, h: cardH,
      fill: { color: COLORS.card },
      line: { color: COLORS.border, pt: 0.5 },
    });
    sl.addText(c.title, {
      x: x + 0.2, y: y + 0.12, w: cardW - 0.4, h: 0.35,
      fontSize: 15, fontFace: F.heading, bold: true,
      color: COLORS.accent, margin: 0,
    });
    sl.addText(c.body, {
      x: x + 0.2, y: y + 0.5, w: cardW - 0.4, h: 0.85,
      fontSize: 12, fontFace: F.body, color: COLORS.text, margin: 0, valign: 'top',
    });
    sl.addText(c.ref, {
      x: x + 0.2, y: y + 1.36, w: cardW - 0.4, h: 0.28,
      fontSize: 10, fontFace: F.body, italic: true,
      color: COLORS.textMuted, margin: 0,
    });
  });

  addFooter(sl, 4, TOTAL);
}

// =================== Slide 5 - System design ===================
{
  const sl = deck.addSlide();
  sl.background = { color: COLORS.bg };
  addTitleBar(sl, 'System design: pluggable heuristic architecture');

  // Embed architecture image
  const archPath = '/tmp/Heuristics-Project_Anthony-Kwasi/charts_phase3/chart6_architecture.png';
  if (fs.existsSync(archPath)) {
    sl.addImage({ path: archPath, x: 0.4, y: 1.25, w: 6.2, h: 3.7, sizing: { type: 'contain', w: 6.2, h: 3.7 } });
  }

  sl.addText('Key idea', {
    x: 6.7, y: 1.3, w: 2.9, h: 0.35,
    fontSize: 16, fontFace: F.heading, bold: true,
    color: COLORS.accent, margin: 0,
  });
  const txt = [
    'Solvers accept a heuristic callable, not a hard-coded function.',
    'Adding a new heuristic = one import line, one CLI flag.',
    'Same code path tested in BFS, A*, and IDA*.',
    'Ablation becomes a one-line change.',
  ];
  sl.addText(
    txt.map((p, i) => ({
      text: p, options: { breakLine: i < txt.length - 1, bullet: { code: '2022' } },
    })),
    {
      x: 6.7, y: 1.7, w: 2.9, h: 3.3,
      fontSize: 12, fontFace: F.body, color: COLORS.text,
      paraSpaceAfter: 6, margin: 0, valign: 'top',
    },
  );

  addFooter(sl, 5, TOTAL);
}

// =================== Slide 6 - Three heuristics ===================
{
  const sl = deck.addSlide();
  sl.background = { color: COLORS.bg };
  addTitleBar(sl, 'Three admissible heuristics');

  const cols = [
    { title: 'Manhattan distance', color: COLORS.manhattan,
      lines: [
        'Sum |dr| + |dc| per tile',
        'O(n^2) evaluation',
        'Ignores tile interactions',
        'Baseline for all comparisons',
      ],
      ref: 'Russell & Norvig 2021' },
    { title: 'Linear Conflict', color: COLORS.linearConflict,
      lines: [
        'Manhattan + 2 per row/col conflict',
        'Greedy max-conflict removal',
        'Captures pairwise interactions',
        'Typical 3-5x speedup on 4x4',
      ],
      ref: 'Hansson, Mayer & Yung 1992' },
    { title: 'Disjoint PDB (4-4-4-3)', color: COLORS.pdb,
      lines: [
        '4 disjoint tile groups',
        '0-1 BFS in projected space',
        'Sum of group lookups (additive)',
        '1.6 M entries, ~4 s build',
      ],
      ref: 'Korf & Felner 2002' },
  ];

  const cardW = 3.0, cardH = 3.5;
  cols.forEach((c, i) => {
    const x = 0.45 + i * 3.2;
    const y = 1.3;
    // top accent block
    sl.addShape(deck.shapes.RECTANGLE, {
      x, y, w: cardW, h: 0.5,
      fill: { color: c.color }, line: { color: c.color },
    });
    sl.addText(c.title, {
      x: x + 0.15, y: y + 0.05, w: cardW - 0.3, h: 0.4,
      fontSize: 14, fontFace: F.heading, bold: true,
      color: 'FFFFFF', margin: 0,
    });
    // body
    sl.addShape(deck.shapes.RECTANGLE, {
      x, y: y + 0.5, w: cardW, h: cardH - 0.5,
      fill: { color: COLORS.card },
      line: { color: COLORS.border, pt: 0.5 },
    });
    sl.addText(
      c.lines.map((p, j) => ({
        text: p, options: { breakLine: j < c.lines.length - 1, bullet: { code: '2022' } },
      })),
      {
        x: x + 0.18, y: y + 0.65, w: cardW - 0.36, h: 2.2,
        fontSize: 12, fontFace: F.body, color: COLORS.text,
        paraSpaceAfter: 8, margin: 0, valign: 'top',
      },
    );
    sl.addText(c.ref, {
      x: x + 0.18, y: y + cardH - 0.45, w: cardW - 0.36, h: 0.3,
      fontSize: 10, fontFace: F.body, italic: true,
      color: COLORS.textMuted, margin: 0,
    });
  });

  addFooter(sl, 6, TOTAL);
}

// =================== Slide 7 - Experimental setup ===================
{
  const sl = deck.addSlide();
  sl.background = { color: COLORS.bg };
  addTitleBar(sl, 'Experimental setup');

  // Left: methodology bullets
  sl.addText('Protocol', {
    x: 0.5, y: 1.3, w: 4.5, h: 0.4,
    fontSize: 18, fontFace: F.heading, bold: true,
    color: COLORS.text, margin: 0,
  });
  const protocol = [
    'Random walk from goal -> guaranteed solvable instances',
    'Three scramble depths: 20, 30, 50',
    '50 instances per cell at d=20/30; 30 at d=50',
    'Per-search caps: 5-10 M node expansions',
    'Bootstrap mean and 95% CI, 1000 resamples',
    'Pure Python 3.9 - no C extensions',
  ];
  sl.addText(
    protocol.map((p, i) => ({ text: p, options: { breakLine: i < protocol.length - 1, bullet: { code: '2022' } } })),
    {
      x: 0.5, y: 1.75, w: 4.5, h: 3.2,
      fontSize: 13, fontFace: F.body, color: COLORS.text,
      paraSpaceAfter: 6, margin: 0, valign: 'top',
    },
  );

  // Right: seeds card
  sl.addShape(deck.shapes.RECTANGLE, {
    x: 5.4, y: 1.3, w: 4.1, h: 3.5,
    fill: { color: COLORS.card }, line: { color: COLORS.border, pt: 0.5 },
  });
  sl.addText('Reproducibility seeds', {
    x: 5.55, y: 1.4, w: 3.8, h: 0.4,
    fontSize: 16, fontFace: F.heading, bold: true,
    color: COLORS.accent, margin: 0,
  });
  const seedRows = [
    ['Phase 2 main', '42'],
    ['3x3 depth sweep', '99'],
    ['4x4 depth sweep', '77'],
    ['Phase 3 ablation', '1234'],
  ];
  seedRows.forEach(([k, v], i) => {
    const y = 1.95 + i * 0.45;
    sl.addText(k, {
      x: 5.55, y, w: 2.6, h: 0.35,
      fontSize: 13, fontFace: F.body, color: COLORS.text, margin: 0,
    });
    sl.addText(v, {
      x: 8.15, y, w: 1.2, h: 0.35,
      fontSize: 13, fontFace: F.body, bold: true,
      color: COLORS.accent, margin: 0, align: 'right',
    });
  });
  sl.addText('Running any script twice produces identical metrics.', {
    x: 5.55, y: 4.1, w: 3.8, h: 0.6,
    fontSize: 11, fontFace: F.body, italic: true,
    color: COLORS.textMuted, margin: 0,
  });

  addFooter(sl, 7, TOTAL);
}

// =================== Slide 8 - Headline result ===================
{
  const sl = deck.addSlide();
  sl.background = { color: COLORS.bgDark };

  sl.addText('Headline result', {
    x: 0.5, y: 0.4, w: 9, h: 0.5,
    fontSize: 16, fontFace: F.body, color: COLORS.textMutedOnDark,
    margin: 0, align: 'left',
  });
  sl.addText('15.2x', {
    x: 0.5, y: 0.95, w: 9, h: 1.7,
    fontSize: 180, fontFace: F.heading, bold: true,
    color: COLORS.accentLight, margin: 0, align: 'left',
  });
  sl.addText('fewer A* nodes expanded by Disjoint PDB vs Manhattan', {
    x: 0.5, y: 2.75, w: 9, h: 0.55,
    fontSize: 22, fontFace: F.body, color: COLORS.textOnDark,
    margin: 0, align: 'left',
  });
  sl.addText('at scramble depth 50 - 30 random instances, all solved optimally', {
    x: 0.5, y: 3.3, w: 9, h: 0.4,
    fontSize: 14, fontFace: F.body, italic: true, color: COLORS.textMutedOnDark,
    margin: 0, align: 'left',
  });

  // Three sub-stats
  const subs = [
    ['9.7x', 'wall-clock speedup'],
    ['3.5x', 'Linear Conflict speedup'],
    ['100%', 'admissibility preserved'],
  ];
  subs.forEach(([big, lab], i) => {
    const x = 0.5 + i * 3.2;
    const y = 4.1;
    sl.addText(big, {
      x, y, w: 2.9, h: 0.55,
      fontSize: 36, fontFace: F.heading, bold: true,
      color: COLORS.accentLight, margin: 0, align: 'left',
    });
    sl.addText(lab, {
      x, y: y + 0.55, w: 2.9, h: 0.35,
      fontSize: 12, fontFace: F.body, color: COLORS.textMutedOnDark, margin: 0, align: 'left',
    });
  });
}

// =================== Slide 9 - Speedup chart ===================
{
  const sl = deck.addSlide();
  sl.background = { color: COLORS.bg };
  addTitleBar(sl, 'Node-expansion speedup grows with depth');

  const chartPath = '/tmp/Heuristics-Project_Anthony-Kwasi/charts_phase3/chart3_speedup_vs_baseline.png';
  if (fs.existsSync(chartPath)) {
    sl.addImage({ path: chartPath, x: 0.4, y: 1.25, w: 6.2, h: 3.7, sizing: { type: 'contain', w: 6.2, h: 3.7 } });
  } else {
    console.error('MISSING speedup chart:', chartPath);
  }

  sl.addText('Read', {
    x: 6.8, y: 1.3, w: 2.7, h: 0.35,
    fontSize: 16, fontFace: F.heading, bold: true,
    color: COLORS.accent, margin: 0,
  });
  const reads = [
    'Linear Conflict: steady 1.5-3.5x',
    'Disjoint PDB: 2.7x at d=20 grows to 15.2x at d=50',
    'Gap widens because Manhattan error scales with depth',
    'PDB captures within-group exact costs',
  ];
  sl.addText(
    reads.map((p, i) => ({ text: p, options: { breakLine: i < reads.length - 1, bullet: { code: '2022' } } })),
    {
      x: 6.8, y: 1.75, w: 2.7, h: 3.2,
      fontSize: 12, fontFace: F.body, color: COLORS.text,
      paraSpaceAfter: 8, margin: 0, valign: 'top',
    },
  );

  addFooter(sl, 9, TOTAL);
}

// =================== Slide 10 - Results table ===================
{
  const sl = deck.addSlide();
  sl.background = { color: COLORS.bg };
  addTitleBar(sl, 'Results: A* nodes expanded with 95% CI');

  const header = ['Depth', 'Heuristic', 'Solved', 'Mean nodes', '95% CI'];
  const rows = [
    ['20', 'Manhattan', '50/50', '268', '[203, 343]'],
    ['20', 'Linear Conflict', '50/50', '182', '[141, 229]'],
    ['20', 'Disjoint PDB', '50/50', '100', '[72, 130]'],
    ['30', 'Manhattan', '50/50', '5,896', '[3,758, 8,425]'],
    ['30', 'Linear Conflict', '50/50', '2,328', '[1,528, 3,263]'],
    ['30', 'Disjoint PDB', '50/50', '1,012', '[634, 1,467]'],
    ['50', 'Manhattan', '30/30', '206,058', '[80,300, 348,433]'],
    ['50', 'Linear Conflict', '30/30', '58,840', '[21,729, 101,422]'],
    ['50', 'Disjoint PDB', '30/30', '13,600', '[5,980, 22,300]'],
  ];

  const headerOpts = {
    bold: true, fontSize: 12, fontFace: F.body,
    color: 'FFFFFF', fill: { color: COLORS.accent },
    align: 'center', valign: 'middle',
    border: { type: 'solid', color: COLORS.border, pt: 0.5 },
  };
  const cellOpts = (extraFill) => ({
    fontSize: 12, fontFace: F.body, color: COLORS.text,
    align: 'center', valign: 'middle',
    fill: { color: extraFill || 'FFFFFF' },
    border: { type: 'solid', color: COLORS.border, pt: 0.5 },
  });

  const tableData = [
    header.map(h => ({ text: h, options: headerOpts })),
    ...rows.map((r, i) => {
      const isPdb = r[1] === 'Disjoint PDB';
      const baseFill = isPdb ? 'E6F0F1' : (i % 2 === 0 ? 'FBFBF9' : 'FFFFFF');
      return r.map((c, j) => ({
        text: c,
        options: { ...cellOpts(baseFill), bold: isPdb && j >= 3 },
      }));
    }),
  ];

  sl.addTable(tableData, {
    x: 0.5, y: 1.25, w: 9.0,
    colW: [0.9, 2.2, 1.2, 1.6, 3.1],
    rowH: 0.34,
    fontSize: 12,
  });

  sl.addText('Solution depths matched across all heuristics - admissibility confirmed empirically.', {
    x: 0.5, y: 4.85, w: 9, h: 0.35,
    fontSize: 11, fontFace: F.body, italic: true,
    color: COLORS.textMuted, margin: 0,
  });

  addFooter(sl, 10, TOTAL);
}

// =================== Slide 11 - Analysis ===================
{
  const sl = deck.addSlide();
  sl.background = { color: COLORS.bg };
  addTitleBar(sl, 'Why does PDB win at depth?');

  // Left: scaling chart
  const chartPath = '/tmp/Heuristics-Project_Anthony-Kwasi/charts_phase3/chart5_scaling_curve.png';
  if (fs.existsSync(chartPath)) {
    sl.addImage({ path: chartPath, x: 0.4, y: 1.25, w: 5.5, h: 3.7, sizing: { type: 'contain', w: 5.5, h: 3.7 } });
  } else {
    console.error('MISSING scaling chart:', chartPath);
  }

  // Right: explanation
  sl.addText('Three reinforcing reasons', {
    x: 6.1, y: 1.25, w: 3.6, h: 0.4,
    fontSize: 16, fontFace: F.heading, bold: true,
    color: COLORS.accent, margin: 0,
  });
  const reasons = [
    [ 'Heuristic error.',
      'Manhattan ignores tile interactions; its error grows roughly linearly with depth.' ],
    [ 'Captured structure.',
      'PDB stores exact within-group cost - the interaction Manhattan misses.' ],
    [ 'Per-call cost.',
      'PDB lookup = single dict access. Linear Conflict pays an inner loop per call.' ],
  ];
  reasons.forEach(([title, body], i) => {
    const y = 1.7 + i * 1.05;
    sl.addText(title, {
      x: 6.1, y, w: 3.6, h: 0.3,
      fontSize: 13, fontFace: F.body, bold: true, color: COLORS.text, margin: 0,
    });
    sl.addText(body, {
      x: 6.1, y: y + 0.3, w: 3.6, h: 0.7,
      fontSize: 12, fontFace: F.body, color: COLORS.textMuted, margin: 0, valign: 'top',
    });
  });

  addFooter(sl, 11, TOTAL);
}

// =================== Slide 12 - Limitations ===================
{
  const sl = deck.addSlide();
  sl.background = { color: COLORS.bg };
  addTitleBar(sl, 'What is left on the table');

  const cards = [
    { title: 'Pure Python overhead',
      body: 'Absolute runtimes lag C/C++; ratios are the meaningful quantity.' },
    { title: 'Non-canonical partition',
      body: '4-4-4-3 fits in 1.6 M entries. 7-8 partition would dominate but needs a multi-hour build.' },
    { title: 'Depth ceiling',
      body: 'Only random instances tested up to d=50. Pathological d~80 instances unexplored.' },
    { title: 'No tie-breaking',
      body: 'Asai-Fukunaga prefer-larger-g shown to help. Not implemented in this deliverable.' },
  ];

  const cardW = 4.2, cardH = 1.55;
  cards.forEach((c, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.5 + col * 4.55;
    const y = 1.4 + row * 1.85;
    sl.addShape(deck.shapes.RECTANGLE, {
      x, y, w: cardW, h: cardH,
      fill: { color: COLORS.card }, line: { color: COLORS.border, pt: 0.5 },
    });
    sl.addText(c.title, {
      x: x + 0.2, y: y + 0.15, w: cardW - 0.4, h: 0.35,
      fontSize: 14, fontFace: F.heading, bold: true,
      color: COLORS.accent, margin: 0,
    });
    sl.addText(c.body, {
      x: x + 0.2, y: y + 0.55, w: cardW - 0.4, h: 0.95,
      fontSize: 12, fontFace: F.body, color: COLORS.text, margin: 0, valign: 'top',
    });
  });

  addFooter(sl, 12, TOTAL);
}

// =================== Slide 13 - Conclusion / Future ===================
{
  const sl = deck.addSlide();
  sl.background = { color: COLORS.bgDark };

  sl.addText('Takeaways', {
    x: 0.6, y: 0.5, w: 9, h: 0.55,
    fontSize: 32, fontFace: F.heading, bold: true,
    color: COLORS.textOnDark, margin: 0,
  });

  // Three key takeaways
  const takeaways = [
    ['1', 'Pluggable heuristics make ablation cheap.', 'One callable, one CLI flag - nothing else changes.'],
    ['2', 'Disjoint PDB delivers 15.2x at d=50.', 'Wall-clock speedup of 9.7x. Strict optimality preserved.'],
    ['3', 'Pure Python is enough for the science.', 'Ratios are reproducible; 4 s build time keeps grading easy.'],
  ];
  takeaways.forEach(([n, t, sub], i) => {
    const y = 1.35 + i * 0.95;
    sl.addText(n, {
      x: 0.6, y, w: 0.5, h: 0.7,
      fontSize: 36, fontFace: F.heading, bold: true,
      color: COLORS.accentLight, margin: 0, align: 'left',
    });
    sl.addText(t, {
      x: 1.2, y, w: 8.2, h: 0.4,
      fontSize: 18, fontFace: F.body, bold: true,
      color: COLORS.textOnDark, margin: 0, align: 'left',
    });
    sl.addText(sub, {
      x: 1.2, y: y + 0.4, w: 8.2, h: 0.4,
      fontSize: 13, fontFace: F.body,
      color: COLORS.textMutedOnDark, margin: 0, align: 'left',
    });
  });

  // Future work strip
  sl.addText('Future work', {
    x: 0.6, y: 4.4, w: 9, h: 0.3,
    fontSize: 13, fontFace: F.heading, bold: true,
    color: COLORS.accentLight, margin: 0,
  });
  sl.addText('Canonical 5-5-5 / 7-8 PDB  |  Asai-Fukunaga tie-breaking  |  Transposition tables in IDA*  |  Generalise to 24-puzzle', {
    x: 0.6, y: 4.7, w: 9, h: 0.35,
    fontSize: 12, fontFace: F.body,
    color: COLORS.textMutedOnDark, margin: 0,
  });

  // Repo link
  sl.addText([
    { text: 'Repo: ', options: { color: COLORS.textMutedOnDark } },
    { text: 'github.com/AnSikwa/Heuristics-Project_Anthony-Kwasi',
      options: { color: COLORS.accentLight, hyperlink: { url: 'https://github.com/AnSikwa/Heuristics-Project_Anthony-Kwasi' } } },
  ], {
    x: 0.6, y: 5.15, w: 9, h: 0.35,
    fontSize: 12, fontFace: F.body, margin: 0, align: 'left',
  });
}

// ---- Write ----
(async () => {
  const out = '/tmp/Heuristics-Project_Anthony-Kwasi/CS57200_Final_Slides.pptx';
  await deck.writeFile({ fileName: out });
  console.log('Wrote', out);
})();
