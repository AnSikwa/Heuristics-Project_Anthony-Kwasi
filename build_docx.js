// Build CS57200_Final_Report.docx from scratch.
// Mirrors the content of CS57200_Final_Report.pdf with proper Word structure:
// real headings, real tables, embedded charts, clickable hyperlinks.

const fs = require('fs');
const docx = require('docx');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
  AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType, PageBreak,
  ExternalHyperlink, LevelFormat, convertInchesToTwip,
} = docx;

// ---- Design tokens ----
const COLORS = {
  text: '28251D',
  textMuted: '7A7974',
  accent: '01696F',
  border: 'D4D1CA',
  headerFill: 'E6F0F1',
  altRow: 'FBFBF9',
  tableTop: '01696F',
};
const FONT_HEAD = 'Arial';
const FONT_BODY = 'Arial';

// US Letter page in DXA
const PAGE_W = 12240, PAGE_H = 15840;
const MARGIN = 1080; // 0.75"
const CONTENT_W = PAGE_W - 2 * MARGIN;

// ---- Helpers ----
const para = (text, opts = {}) => new Paragraph({
  spacing: { before: 100, after: 100, line: 300 },
  alignment: opts.align || AlignmentType.JUSTIFIED,
  ...opts.paraOpts,
  children: Array.isArray(text)
    ? text
    : [new TextRun({ text, font: FONT_BODY, size: 22, color: COLORS.text, ...opts.run })],
});

const h1 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 360, after: 160 },
  children: [new TextRun({ text, font: FONT_HEAD, size: 32, bold: true, color: COLORS.accent })],
});
const h2 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  spacing: { before: 240, after: 120 },
  children: [new TextRun({ text, font: FONT_HEAD, size: 26, bold: true, color: COLORS.text })],
});
const h3 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_3,
  spacing: { before: 180, after: 100 },
  children: [new TextRun({ text, font: FONT_HEAD, size: 22, bold: true, color: COLORS.text })],
});
const bullet = (text) => new Paragraph({
  numbering: { reference: 'bullets', level: 0 },
  spacing: { before: 60, after: 60, line: 280 },
  children: Array.isArray(text)
    ? text
    : [new TextRun({ text, font: FONT_BODY, size: 22, color: COLORS.text })],
});
const caption = (text) => new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 80, after: 200 },
  children: [new TextRun({ text, italics: true, font: FONT_BODY, size: 20, color: COLORS.textMuted })],
});
const link = (text, url) => new ExternalHyperlink({
  link: url,
  children: [new TextRun({ text, font: FONT_BODY, size: 22, color: '01696F', underline: { type: 'single', color: '01696F' } })],
});

const thinBorder = { style: BorderStyle.SINGLE, size: 4, color: COLORS.border };
const allBorders = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder };

function tableCell({ text, width, fill, bold = false, color, align = AlignmentType.LEFT }) {
  return new TableCell({
    borders: allBorders,
    width: { size: width, type: WidthType.DXA },
    shading: fill ? { fill, type: ShadingType.CLEAR, color: 'auto' } : undefined,
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({
      alignment: align,
      spacing: { before: 0, after: 0 },
      children: [new TextRun({
        text: String(text),
        font: FONT_BODY,
        size: 20,
        bold,
        color: color || (fill === COLORS.tableTop ? 'FFFFFF' : COLORS.text),
      })],
    })],
  });
}

function buildTable(headers, rows, colWidths, opts = {}) {
  const tableW = colWidths.reduce((a, b) => a + b, 0);
  const headerRow = new TableRow({
    tableHeader: true,
    children: headers.map((h, i) => tableCell({
      text: h, width: colWidths[i], fill: COLORS.tableTop, bold: true, color: 'FFFFFF',
      align: opts.align?.[i] || AlignmentType.CENTER,
    })),
  });
  const dataRows = rows.map((row, idx) => {
    const isHighlight = opts.highlight && opts.highlight(row, idx);
    const fill = isHighlight ? COLORS.headerFill : (idx % 2 === 0 ? COLORS.altRow : 'FFFFFF');
    return new TableRow({
      children: row.map((cell, i) => tableCell({
        text: cell, width: colWidths[i], fill, bold: isHighlight && i >= (opts.boldFromCol || 0),
        align: opts.align?.[i] || AlignmentType.LEFT,
      })),
    });
  });
  return new Table({
    width: { size: tableW, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [headerRow, ...dataRows],
  });
}

function image(path, width, height) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 160, after: 80 },
    children: [new ImageRun({
      type: 'png',
      data: fs.readFileSync(path),
      transformation: { width, height },
      altText: { title: path.split('/').pop(), description: 'Phase 3 figure', name: path.split('/').pop() },
    })],
  });
}

// ---- Content ----
const sec = (...nodes) => nodes;
const root = '/tmp/Heuristics-Project_Anthony-Kwasi/charts_phase3';

// ----- Cover -----
const cover = [
  new Paragraph({ spacing: { before: 1800 }, children: [new TextRun('')] }),
  new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 0, after: 200 },
    children: [new TextRun({ text: 'Heuristic A* Search for Large Sliding Puzzles', font: FONT_HEAD, size: 48, bold: true, color: COLORS.accent })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 0, after: 200 },
    children: [new TextRun({ text: 'Using Advanced Heuristics', font: FONT_HEAD, size: 48, bold: true, color: COLORS.accent })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 0, after: 800 },
    children: [new TextRun({ text: 'Final Project Report - Track B: Search & Optimization', font: FONT_BODY, italics: true, size: 26, color: COLORS.textMuted })],
  }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
    children: [new TextRun({ text: 'Anthony Kwasi', font: FONT_BODY, size: 26, color: COLORS.text })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
    children: [new TextRun({ text: 'CS 57200: Heuristic Problem Solving', font: FONT_BODY, size: 24, color: COLORS.text })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 },
    children: [new TextRun({ text: 'Purdue University - Spring 2026', font: FONT_BODY, size: 24, color: COLORS.text })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
    children: [
      new TextRun({ text: 'Repository: ', font: FONT_BODY, bold: true, size: 22, color: COLORS.text }),
      link('github.com/AnSikwa/Heuristics-Project_Anthony-Kwasi',
           'https://github.com/AnSikwa/Heuristics-Project_Anthony-Kwasi'),
    ],
  }),
  para([
    new TextRun({ text: 'Abstract. ', font: FONT_BODY, bold: true, size: 22, color: COLORS.text }),
    new TextRun({ text:
      'We present a unified experimental study of informed search algorithms (BFS, A*, IDA*) and admissible heuristics (Manhattan distance, Linear Conflict, Disjoint Pattern Databases) for the 8- and 15-tile sliding puzzles. On the 4x4 puzzle at scramble depth 50, the disjoint additive PDB heuristic (4-4-4-3 partition) reduces A* node expansions by 15.2x relative to Manhattan distance and wall-clock time by 9.7x while preserving optimality. Linear Conflict yields a 3.5x node reduction at the same depth. Across 30-50 random instances per cell, all algorithm/heuristic combinations agree on solution depth, empirically confirming admissibility.',
      font: FONT_BODY, size: 22, color: COLORS.text }),
  ]),
];

// ----- 1. Introduction -----
const intro = [
  new Paragraph({ children: [new PageBreak()] }),
  h1('1. Introduction & Problem Formulation'),
  para('The n-puzzle, comprising n^2 - 1 numbered tiles on an n x n grid with one blank space, is a canonical benchmark for heuristic search. The 4x4 instance (15-puzzle) admits roughly 16!/2 = 1.05 x 10^13 reachable states with optimal solutions of up to 80 moves, and the 5x5 instance (24-puzzle) admits 25!/2 = 7.76 x 10^24 states - far beyond brute-force search.'),
  para([
    new TextRun({ text: 'Research question. ', font: FONT_BODY, bold: true, size: 22, color: COLORS.text }),
    new TextRun({ text: 'How do increasingly informed admissible heuristics (Manhattan distance, Manhattan + Linear Conflict, Disjoint Pattern Databases) compare on the same set of random 15-puzzle instances when paired with A* and IDA*, in terms of node expansions, wall-clock runtime, and solution optimality?', font: FONT_BODY, size: 22, color: COLORS.text }),
  ]),
  h2('1.1 Formal Specification'),
  bullet([new TextRun({ text: 'State: ', font: FONT_BODY, bold: true, size: 22 }), new TextRun({ text: 'immutable tuple of length n^2; tile 0 denotes the blank.', font: FONT_BODY, size: 22 })]),
  bullet([new TextRun({ text: 'Initial state: ', font: FONT_BODY, bold: true, size: 22 }), new TextRun({ text: 'any solvable permutation, generated here by a seeded random walk from the goal so solvability is structural rather than parity-checked.', font: FONT_BODY, size: 22 })]),
  bullet([new TextRun({ text: 'Actions: ', font: FONT_BODY, bold: true, size: 22 }), new TextRun({ text: 'sliding the blank up, down, left, or right within the grid (branching factor at most 4; average ~2.13 on 4x4).', font: FONT_BODY, size: 22 })]),
  bullet([new TextRun({ text: 'Transition cost: ', font: FONT_BODY, bold: true, size: 22 }), new TextRun({ text: 'uniform unit cost per move.', font: FONT_BODY, size: 22 })]),
  bullet([new TextRun({ text: 'Goal test: ', font: FONT_BODY, bold: true, size: 22 }), new TextRun({ text: 'state == (1, 2, ..., n^2 - 1, 0).', font: FONT_BODY, size: 22 })]),
  bullet([new TextRun({ text: 'Solution: ', font: FONT_BODY, bold: true, size: 22 }), new TextRun({ text: 'a minimum-length sequence of legal actions from the start to the goal.', font: FONT_BODY, size: 22 })]),

  h2('1.2 Contributions'),
  bullet('Three search algorithms - BFS (uninformed baseline), A*, and IDA* - with a shared, pluggable heuristic interface.'),
  bullet('Three admissible heuristics: Manhattan distance, Manhattan + Linear Conflict, and a disjoint additive Pattern Database under a 4-4-4-3 partition of the 15 tiles.'),
  bullet('A controlled ablation across scramble depths {20, 30, 50} on 30-50 instances per cell, with bootstrap 95% confidence intervals.'),
  bullet('Empirical confirmation that solution depths agree across heuristics (admissibility check) and quantitative speedup curves showing the PDB heuristic accelerates A* by up to 15.2x.'),

  h2('1.3 Scope changes since Milestone 1'),
  para('Milestone 1 proposed four enhancements: disjoint PDBs, IDA*, tie-breaking strategies, and transposition tables. The final deliverable retains and ships disjoint PDBs and IDA*, adds Linear Conflict (which Milestone 2 listed as a fallback enhancement), and defers tie-breaking and transposition tables to future work. The PDB partition was reduced from the canonical 5-5-5 (~17 M projected states) to a 4-4-4-3 partition (~1.6 M states) so that the database can be built in pure Python in seconds; this matches the Milestone 2 contingency clause and still yields the headline result.'),
];

// ----- 2. Related Work -----
const related = [
  h1('2. Related Work'),
  h3('2.1 Foundational algorithms'),
  para('Hart, Nilsson and Raphael [1] introduced A*, evaluating each node by f(n) = g(n) + h(n). When h is admissible, A* returns optimal solutions; consistency further guarantees no node is re-expanded in graph search. Korf [2] introduced Iterative-Deepening A* (IDA*), which trades repeated DFS sweeps for O(d) memory and was the first method to solve random 15-puzzle instances within practical limits.'),
  h3('2.2 Manhattan distance'),
  para('Manhattan distance sums each tile\'s grid displacement from its goal cell. Russell & Norvig [3] derive it as the exact cost of a relaxed problem in which tiles may overlap. It is admissible and consistent but ignores tile interactions, leading to large search trees.'),
  h3('2.3 Linear Conflict'),
  para('Hansson, Mayer and Yung [4] augment Manhattan distance with the linear conflict bonus: when two tiles share their goal row (or column) but are in reversed order, at least one must move out of the line and back, adding two moves. Adding 2 per detected conflict preserves admissibility, and the heuristic typically reduces 15-puzzle solve times by 3-5x. Qin & Zhang [5] re-confirmed this gain on modern hardware.'),
  h3('2.4 Pattern Databases'),
  para('Culberson & Schaeffer [6] precomputed the exact cost of solving sub-problems involving subsets of tiles, achieving roughly 1000x node-expansion reduction with a fringe-pattern database. Korf & Felner [7] extended this with disjoint additive PDBs that partition the tiles into non-overlapping groups whose costs may be summed; their 7-8 partition delivered over 2000x speedup on the 15-puzzle. Felner, Korf & Hanan [8] dynamically partitioned the tiles per state and solved 50 random 24-puzzle instances optimally. Holte et al. [9] showed how maximising over multiple PDBs further improves runtime.'),
  h3('2.5 Tie-breaking and IDA* enhancements'),
  para('Asai & Fukunaga [10] showed that, even with ties on f-value, expanding nodes with the largest g first reduces the total expansion count without compromising optimality. Edelkamp & Schroedl [11] summarise transposition-table augmentations of IDA*, which trade memory for fewer redundant expansions.'),
  h3('2.6 Gap and contribution'),
  para('Despite extensive prior work on individual techniques, there is little published work that directly compares Manhattan, Linear Conflict and a disjoint additive PDB on the same set of random 15-puzzle instances with both A* and IDA*, reporting 95% confidence intervals across three scramble depths. This report contributes such a controlled ablation and an open, reproducible Python implementation.'),
];

// ----- 3. System design -----
const system = [
  h1('3. System Design & Implementation'),
  para('Figure 1 shows the high-level architecture. The system has four layers: an instance generator, a state representation, a set of pluggable heuristics, and a set of search algorithms. All searches accept a heuristic callable so the same code path is reused across all enhancements.'),
  image(`${root}/chart6_architecture.png`, 540, 360),
  caption('Figure 1. System architecture for Phase 3.'),

  h3('3.1 State representation'),
  para('Each state is a Python tuple of length n^2 with 0 indicating the blank. Tuples are immutable and hashable, so they can serve as dictionary keys without a separate visited set. The branching factor never exceeds 4, and parent-state pruning reduces it by one along any non-trivial path.'),
  h3('3.2 Algorithms'),
  para([
    new TextRun({ text: 'BFS (uninformed baseline) ', font: FONT_BODY, bold: true, size: 22 }),
    new TextRun({ text: 'uses a deque frontier and a predecessor map for path reconstruction; on the 3x3 puzzle it always returns optimal-length paths because edges have unit cost.', font: FONT_BODY, size: 22 }),
  ]),
  para([
    new TextRun({ text: 'A* ', font: FONT_BODY, bold: true, size: 22 }),
    new TextRun({ text: 'uses a binary heap ordered by (f, g, state). Lazy deletion skips outdated heap entries when popped, avoiding decrease-key machinery. Tuple comparison lexicographically breaks ties toward smaller g first, which is admissible.', font: FONT_BODY, size: 22 }),
  ]),
  para([
    new TextRun({ text: 'IDA* ', font: FONT_BODY, bold: true, size: 22 }),
    new TextRun({ text: 'runs successive depth-first searches bounded by an f-threshold that grows to the next-smallest f-value after each failed iteration. Memory use is O(d). Parent-state pruning avoids two-cycle oscillation.', font: FONT_BODY, size: 22 }),
  ]),
  h3('3.3 Heuristic stack'),
  para([
    new TextRun({ text: 'Manhattan distance. ', font: FONT_BODY, bold: true, size: 22 }),
    new TextRun({ text: 'Sums |row_i - goal_row_i| + |col_i - goal_col_i| for every non-blank tile. Linear-time evaluation, admissible, consistent.', font: FONT_BODY, size: 22 }),
  ]),
  para([
    new TextRun({ text: 'Manhattan + Linear Conflict. ', font: FONT_BODY, bold: true, size: 22 }),
    new TextRun({ text: 'Adds 2 per linear conflict in rows and columns. Conflicts are counted greedily by repeatedly removing the most-conflicted tile in each line until the line is conflict-free.', font: FONT_BODY, size: 22 }),
  ]),
  para([
    new TextRun({ text: 'Disjoint Pattern Database. ', font: FONT_BODY, bold: true, size: 22 }),
    new TextRun({ text: 'The 15 tiles are partitioned into four disjoint groups {1,2,5,6}, {3,4,7,8}, {9,10,13,14}, {11,12,15}. Each PDB stores, for every reachable projection (blank position, tuple of group-tile positions), the minimum number of group-tile moves needed to reach a goal-aligned projection. The database is built once via a 0-1 BFS from the goal in projected space; group-tile moves cost 1 and non-group-tile moves cost 0. Per-group lookups are summed at search time, which is admissible because each move advances at most one tile.', font: FONT_BODY, size: 22 }),
  ]),
  h3('3.4 Implementation choices'),
  bullet('Pure-Python implementation (no C extensions) for reproducibility and ease of grading.'),
  bullet('PDB partition 4-4-4-3 totalling 1,616,160 entries; full build completes in under 4 seconds on commodity hardware. The canonical 5-5-5 partition (~17 M entries) is exposed but not pre-built because pure-Python build time becomes prohibitive.'),
  bullet('All experiments use fixed RNG seeds; running any script twice produces identical instances and identical metrics.'),
  bullet('Per-search node and recursion limits guard against IDA* stack overflows on very deep instances.'),
];

// ----- 4. Methodology & Results -----
// Table widths: must sum to a single value
const ph2Cols = [1100, 1700, 1500, 1700, 1700, 1660]; // sum 9360
const ph3Cols = [900, 1900, 1100, 1100, 2380, 1980]; // sum 9360

const ph2Rows = [
  ['3x3', 'BFS',  '73,865', '21.7', '140.91', '100/100'],
  ['3x3', 'A*',   '1,564',  '21.7', '8.57',   '100/100'],
  ['3x3', 'IDA*', '2,062',  '21.7', '8.75',   '100/100'],
  ['4x4', 'A*',   '212',    '18.7', '1.79',   '100/100'],
  ['4x4', 'IDA*', '177',    '18.7', '1.28',   '100/100'],
];

const ph3Rows = [
  ['20', 'Manhattan',       'A*',   '50/50', '268.4 [203.3, 343.4]',           '2.49 [1.82, 3.27]'],
  ['20', 'Manhattan',       'IDA*', '50/50', '259.2 [184.4, 347.9]',           '2.01 [1.41, 2.70]'],
  ['20', 'Linear Conflict', 'A*',   '50/50', '182.1 [140.8, 229.4]',           '6.40 [5.02, 8.03]'],
  ['20', 'Linear Conflict', 'IDA*', '50/50', '178.5 [129.3, 237.2]',           '6.09 [4.40, 8.06]'],
  ['20', 'Disjoint PDB',    'A*',   '50/50', '100.2 [72.1, 130.2]',            '2.02 [1.46, 2.61]'],
  ['20', 'Disjoint PDB',    'IDA*', '50/50', '94.7 [62.1, 130.6]',             '1.63 [1.06, 2.27]'],
  ['30', 'Manhattan',       'A*',   '50/50', '5,895.7 [3,758.3, 8,425.0]',     '60.88 [37.76, 88.50]'],
  ['30', 'Manhattan',       'IDA*', '50/50', '7,675.9 [4,488.5, 11,817.1]',    '59.61 [34.61, 91.44]'],
  ['30', 'Linear Conflict', 'A*',   '50/50', '2,328.3 [1,527.5, 3,263.2]',     '77.19 [49.88, 109.16]'],
  ['30', 'Linear Conflict', 'IDA*', '50/50', '2,674.8 [1,649.5, 3,886.1]',     '83.89 [51.12, 122.22]'],
  ['30', 'Disjoint PDB',    'A*',   '50/50', '1,012.2 [634.2, 1,467.3]',       '18.89 [11.73, 27.62]'],
  ['30', 'Disjoint PDB',    'IDA*', '50/50', '1,197.1 [605.9, 1,950.7]',       '19.14 [9.67, 31.31]'],
  ['50', 'Manhattan',       'A*',   '30/30', '206,058.2 [80,299.5, 348,432.6]','2,690.11 [1,014.94, 4,564.58]'],
  ['50', 'Manhattan',       'IDA*', '30/30', '450,618.2 [158,558.5, 827,431.4]','3,405.76 [1,177.97, 6,265.28]'],
  ['50', 'Linear Conflict', 'A*',   '30/30', '58,839.9 [21,728.5, 101,421.7]', '1,786.71 [653.54, 3,082.44]'],
  ['50', 'Linear Conflict', 'IDA*', '30/30', '92,697.2 [34,188.2, 163,084.4]', '2,597.11 [976.15, 4,502.83]'],
  ['50', 'Disjoint PDB',    'A*',   '30/30', '13,600.5 [5,979.6, 22,299.5]',   '277.27 [119.30, 458.54]'],
  ['50', 'Disjoint PDB',    'IDA*', '30/30', '17,925.2 [6,781.8, 32,320.5]',   '281.04 [108.76, 503.29]'],
];

const methodology = [
  h1('4. Experimental Methodology & Results'),
  h2('4.1 Methodology'),
  para('We ran three primary experiments. Phase 2 evaluated BFS, A*, and IDA* on the 3x3 (100 instances) and 4x4 (100 instances) puzzles with Manhattan distance only, plus depth-scaling sweeps. Phase 3 (this section) compares Manhattan vs Linear Conflict vs Disjoint PDB on the 15-puzzle at three scramble depths (20, 30, 50). Phase 3 used 50 instances per cell at depths 20 and 30 and 30 instances at depth 50; seed = 1234. Per-search caps were 5-10 million node expansions.'),
  para([
    new TextRun({ text: 'Reproducibility. ', font: FONT_BODY, bold: true, size: 22 }),
    new TextRun({ text: 'Every experiment uses fixed RNG seeds (Phase 2: 42; 3x3 sweep: 99; 4x4 sweep: 77; ablation: 1234) and is deterministic given the Python version. Statistics below report the bootstrap mean with 95% percentile confidence intervals (1000 resamples).', font: FONT_BODY, size: 22 }),
  ]),

  h2('4.2 Phase 2 main results (Manhattan only)'),
  buildTable(
    ['Size', 'Algorithm', 'Mean nodes', 'Mean depth', 'Mean ms', 'Solved'],
    ph2Rows, ph2Cols,
    { align: [AlignmentType.CENTER, AlignmentType.LEFT, AlignmentType.RIGHT, AlignmentType.RIGHT, AlignmentType.RIGHT, AlignmentType.CENTER] },
  ),
  caption('Table 2. Phase 2 baseline. A* expands ~47x fewer nodes than BFS on the 3x3 puzzle; on the 4x4, IDA* outperforms A* at scramble depth 20 because saving memory dominates the cost of re-expanding nodes.'),

  h2('4.3 Phase 3 ablation across heuristics'),
  buildTable(
    ['Depth', 'Heuristic', 'Algorithm', 'Solved', 'Mean nodes [95% CI]', 'Mean ms [95% CI]'],
    ph3Rows, ph3Cols,
    {
      align: [AlignmentType.CENTER, AlignmentType.LEFT, AlignmentType.CENTER, AlignmentType.CENTER, AlignmentType.RIGHT, AlignmentType.RIGHT],
      highlight: (row) => row[1] === 'Disjoint PDB',
      boldFromCol: 4,
    },
  ),
  caption('Table 1. Phase 3 ablation results on the 15-puzzle. Bootstrap 95% confidence intervals (1000 resamples) of the mean across 30-50 random instances per cell. Solution depth matched across all heuristics and algorithms (admissibility check).'),

  h2('4.4 Visual results'),
  image(`${root}/chart1_nodes_by_heuristic.png`, 520, 340),
  caption('Figure 2. Mean A* nodes expanded by heuristic and scramble depth (log scale). Error bars show bootstrap 95% CIs. PDB lies an order of magnitude below Manhattan at depth 50.'),
  image(`${root}/chart3_speedup_vs_baseline.png`, 520, 340),
  caption('Figure 3. Node-expansion speedup over Manhattan baseline. Linear Conflict yields 1.5-3.5x; Disjoint PDB yields 2.7-15.2x and the gap widens with depth.'),
  image(`${root}/chart4_nodes_box.png`, 520, 340),
  caption('Figure 4. Distribution of A* node expansions at scramble depth 50 (log scale). Each box shows the IQR, whiskers the 1.5x IQR range, and the green triangle the mean.'),
  image(`${root}/chart5_scaling_curve.png`, 520, 340),
  caption('Figure 5. Scaling curves for mean A* node expansions vs scramble depth (log scale). The shaded band shows the 95% CI; the PDB curve grows substantially slower than Manhattan.'),
];

// ----- 5. Analysis -----
const analysis = [
  h1('5. Analysis & Interpretation'),
  h3('5.1 Why does PDB win at depth?'),
  para('At scramble depth 50, Linear Conflict achieves a 3.5x reduction in A* node expansions and the 4-4-4-3 disjoint PDB achieves 15.2x; PDB also reduces wall-clock time by 9.7x because each PDB lookup is a single dictionary access whereas Linear Conflict requires an inner loop. The gap widens with depth because the heuristic-to-true-cost gap for Manhattan distance grows roughly linearly with depth, while the PDB captures exact within-group costs and so its error scales sub-linearly.'),
  h3('5.2 Admissibility check'),
  para('All three heuristics produced identical mean solution depths for every scramble depth in Table 1, on every instance. This is the empirical signature of admissibility: a non-admissible heuristic could return shorter (incorrect) paths. Combined with our hand-verified 8-puzzle benchmarks (depths 1, 3 and 28, all matched), this is strong evidence the implementation is correct.'),
  h3('5.3 A* vs IDA* across heuristics'),
  para('IDA* re-expands nodes across iterations but uses O(d) memory. With Manhattan distance, IDA*\'s repeated work hurts at deep scrambles - at depth 50 IDA* expands roughly 2x as many nodes as A*. With the PDB heuristic, the per-iteration node count drops so sharply that IDA*\'s overhead is small in absolute terms; depth-50 IDA*+PDB completes in roughly the same time as A*+PDB while using a fraction of the memory. This is the Korf & Felner observation transferred to a smaller PDB.'),
  h3('5.4 Limitations'),
  bullet('Pure Python keeps absolute runtimes higher than published C/C++ implementations; ratios are the meaningful quantity.'),
  bullet('The 4-4-4-3 partition is non-canonical; the 7-8 or 5-5-5 partitions used by Korf & Felner would yield substantially stronger heuristics at the cost of a multi-hour build.'),
  bullet('Scramble depths beyond 50 cause unpredictable variance; we did not exhaust solvable depth.'),
  bullet('Only random instances were tested; pathological instances (near-maximal optimal solutions ~80 moves) are out of scope.'),
];

// ----- 6. Conclusion & future work -----
const conclusion = [
  h1('6. Conclusion & Future Work'),
  para('We delivered a unified, reproducible heuristic-search testbed for the sliding-tile puzzle with three search algorithms and three admissible heuristics. The headline result is a 15.2x node-expansion speedup of A*+PDB over A*+Manhattan at scramble depth 50, with strict optimality preserved across all comparisons. Linear Conflict is a strictly weaker enhancement (3.5x speedup at the same depth) but is far cheaper to implement and adds no precomputation cost.'),
  para([
    new TextRun({ text: 'Lessons learned. ', font: FONT_BODY, bold: true, size: 22 }),
    new TextRun({ text: 'Pure-Python PDB construction is viable for partitions up to ~5 tiles per group; beyond that, either C extensions or memory-mapped on-disk tables are required. Treating the heuristic as a callable parameter (rather than hard-coding it inside the solver) made the ablation trivial to add and made the search code easier to test.', font: FONT_BODY, size: 22 }),
  ]),
  h3('6.1 Future work'),
  bullet('Build the canonical 5-5-5 or 7-8 PDB partitions with a C extension or numpy-backed flat array, expecting another 5-10x improvement.'),
  bullet('Implement and study Asai-Fukunaga tie-breaking: prefer-larger-g and prefer-smaller-h within an f-bucket, which is independent of the heuristic and orthogonal to PDBs.'),
  bullet('Add transposition tables to IDA* and measure the memory/expansion trade-off across various table sizes.'),
  bullet('Generalise the implementation to the 24-puzzle (5x5), where Manhattan-only IDA* is intractable; this exercises the memory-efficiency rationale for IDA* most clearly.'),
  bullet('Apply the same testbed to learning-based heuristics (e.g., neural cost-to-go regressors) for a head-to-head comparison with classical PDBs.'),
];

// ----- References -----
function refPara(num, body, url) {
  const runs = [
    new TextRun({ text: `[${num}] `, font: FONT_BODY, bold: true, size: 22 }),
    new TextRun({ text: body, font: FONT_BODY, size: 22 }),
  ];
  if (url) {
    runs.push(new TextRun({ text: ' ', font: FONT_BODY, size: 22 }));
    runs.push(new ExternalHyperlink({
      link: url,
      children: [new TextRun({ text: url, font: FONT_BODY, size: 20, color: '01696F', underline: { type: 'single', color: '01696F' } })],
    }));
  }
  return new Paragraph({
    spacing: { before: 80, after: 80 },
    indent: { left: 360, hanging: 360 },
    children: runs,
  });
}

const references = [
  h1('References'),
  refPara(1,  'Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). A formal basis for the heuristic determination of minimum cost paths. IEEE Trans. Systems Science and Cybernetics, 4(2), 100-107.', 'https://doi.org/10.1109/TSSC.1968.300136'),
  refPara(2,  'Korf, R. E. (1985). Depth-first iterative-deepening: an optimal admissible tree search. Artificial Intelligence, 27(1), 97-109.', 'https://doi.org/10.1016/0004-3702(85)90084-0'),
  refPara(3,  'Russell, S. & Norvig, P. (2021). Artificial Intelligence: A Modern Approach (4th ed.). Pearson.', 'https://aima.cs.berkeley.edu/'),
  refPara(4,  'Hansson, O., Mayer, A. & Yung, M. (1992). Generating admissible heuristics by criticising solutions to relaxed models. Artificial Intelligence, 55(1), 29-60.'),
  refPara(5,  'Qin, Z. & Zhang, M. (2025). Solving the sliding puzzle problem using the A* algorithm and comparing heuristic functions. Dean & Francis Academic Publishing.'),
  refPara(6,  'Culberson, J. & Schaeffer, J. (1998). Pattern databases. Computational Intelligence, 14(3), 318-334.', 'https://doi.org/10.1111/0824-7935.00065'),
  refPara(7,  'Korf, R. E. & Felner, A. (2002). Disjoint pattern database heuristics. Artificial Intelligence, 134(1-2), 9-22.'),
  refPara(8,  'Felner, A., Korf, R. E. & Hanan, S. (2004). Additive pattern database heuristics. Journal of Artificial Intelligence Research, 22, 279-318.', 'https://doi.org/10.1613/jair.1480'),
  refPara(9,  'Holte, R. C., Felner, A., Newton, J., Meshulam, R. & Furcy, D. (2006). Maximizing multiple pattern databases speeds up heuristic search. Artificial Intelligence, 170(16-17), 1123-1136.', 'https://doi.org/10.1016/j.artint.2006.10.007'),
  refPara(10, 'Asai, M. & Fukunaga, A. (2018). Analysing tie-breaking strategies for the A* algorithm. Proceedings of IJCAI-2018, 4660-4666.'),
  refPara(11, 'Edelkamp, S. & Schroedl, S. (2012). Heuristic Search: Theory and Applications. Morgan Kaufmann.'),
  refPara(12, 'Kishimoto, A., Fukunaga, A. & Botea, A. (2013). Evaluation of a simple, scalable, parallel best-first search strategy. Artificial Intelligence, 195, 222-248.'),
];

// ----- Appendix -----
const codeFont = { font: 'Consolas', size: 20, color: COLORS.text };
const codeLine = (text) => new Paragraph({
  spacing: { before: 20, after: 20 },
  indent: { left: 360 },
  children: [new TextRun({ text, ...codeFont })],
});

const appendix = [
  h1('Appendix A. Reproducing the results'),
  para('All scripts live in the project root. Python 3.9 or newer is required; install dependencies with pip install -r requirements.txt.'),
  para([new TextRun({ text: 'Phase 2 (BFS / A* / IDA* with Manhattan):', font: FONT_BODY, bold: true, size: 22 })]),
  codeLine('python solver.py'),
  codeLine('python make_charts.py'),
  codeLine('python make_report.py'),
  para([new TextRun({ text: 'Phase 3 (heuristic ablation):', font: FONT_BODY, bold: true, size: 22 })]),
  codeLine('python ablation.py --n 4 --scramble 20 --instances 50 --out ablation_4x4_d20.json'),
  codeLine('python ablation.py --n 4 --scramble 30 --instances 50 --out ablation_4x4_d30.json'),
  codeLine('python ablation.py --n 4 --scramble 50 --instances 30 --out ablation_4x4_d50.json'),
  codeLine('python ablation_charts.py'),
  codeLine('python make_final_report.py'),
];

// ---- Document ----
const report = new Document({
  creator: 'Anthony Kwasi',
  title: 'CS 57200 Final Report - Heuristic A* Search',
  description: 'Final project report for CS 57200 Heuristic Problem Solving',
  styles: {
    default: { document: { run: { font: FONT_BODY, size: 22, color: COLORS.text } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT_HEAD, size: 32, bold: true, color: COLORS.accent },
        paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT_HEAD, size: 26, bold: true, color: COLORS.text },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
      { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT_HEAD, size: 22, bold: true, color: COLORS.text },
        paragraph: { spacing: { before: 180, after: 100 }, outlineLevel: 2 } },
    ],
  },
  numbering: {
    config: [
      {
        reference: 'bullets',
        levels: [
          { level: 0, format: LevelFormat.BULLET, text: '\u2022', alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 540, hanging: 270 } } } },
        ],
      },
    ],
  },
  sections: [
    {
      properties: {
        page: {
          size: { width: PAGE_W, height: PAGE_H },
          margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN },
        },
      },
      children: [
        ...cover,
        ...intro,
        ...related,
        ...system,
        ...methodology,
        ...analysis,
        ...conclusion,
        ...references,
        ...appendix,
      ],
    },
  ],
});

Packer.toBuffer(report).then((buf) => {
  const out = '/tmp/Heuristics-Project_Anthony-Kwasi/CS57200_Final_Report.docx';
  fs.writeFileSync(out, buf);
  console.log('Wrote', out);
});
