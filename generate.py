import json, re, os

TEMPLATE = open('template.html', encoding='utf-8').read()
OUT_DIR = 'solutions'

DIFF_VAR = {'Easy': 'good', 'Medium': 'warn', 'Hard': 'bad'}

def highlight_python(code):
    KEYWORDS = ['def','class','from','import','return','if','elif','else','while','for','in','not','and','or',
                'True','False','None','self','while','break','continue','is']
    BUILTINS = ['len','min','max','sorted','enumerate','range','list','dict','set','int','str','sum','abs']
    lines = code.split('\n')
    out = []
    for line in lines:
        # comment
        comment = ''
        cidx = line.find('#')
        if cidx != -1:
            comment = line[cidx:]
            line = line[:cidx]
        # strings
        line = re.sub(r"(\"[^\"]*\"|'[^']*')", lambda m: f'\x01STR{m.group(0)}\x02', line)
        # numbers
        line = re.sub(r'(?<![\w])(\d+)(?![\w])', lambda m: f'\x01NUM{m.group(1)}\x02', line)
        # keywords
        for kw in KEYWORDS:
            line = re.sub(rf'(?<![\w]){kw}(?![\w])', f'\x01KW{kw}\x02', line)
        # builtins / function-call names (word followed by '(')
        line = re.sub(r'(?<![\w.])([A-Za-z_][A-Za-z0-9_]*)(?=\()', lambda m: f'\x01FN{m.group(1)}\x02' if m.group(1) not in KEYWORDS else m.group(1), line)
        # escape html
        line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # restore tokens to spans
        line = re.sub(r'\x01STR(.*?)\x02', r'<span class="str">\1</span>', line)
        line = re.sub(r'\x01NUM(.*?)\x02', r'<span class="num">\1</span>', line)
        line = re.sub(r'\x01KW(.*?)\x02', r'<span class="kw">\1</span>', line)
        line = re.sub(r'\x01FN(.*?)\x02', r'<span class="fn">\1</span>', line)
        if comment:
            comment = comment.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            line += f'<span class="cm">{comment}</span>'
        out.append(line)
    return '\n'.join(out)

def js_string(code):
    return json.dumps(code)

def render(problem):
    html = TEMPLATE
    html = html.replace('__TITLE__', problem['title'])
    html = html.replace('__SLUG__', problem['slug'])
    html = html.replace('__CATEGORY__', problem['category'])
    html = html.replace('__CATEGORY_URL__', problem['category'])
    html = html.replace('__DIFFICULTY__', problem['difficulty'])
    html = html.replace('__DIFF_VAR__', DIFF_VAR[problem['difficulty']])
    tags_html = ''.join(f'<span class="px-2.5 py-1 rounded-md text-xs font-semibold text-soft" style="background:var(--rail)">{t}</span>' for t in problem['tags'])
    html = html.replace('__TAGS_HTML__', tags_html)
    html = html.replace('__LEETCODE_URL__', problem['leetcode_url'])
    html = html.replace('__STATEMENT_HTML__', problem['statement_html'])
    html = html.replace('__EXAMPLE_HTML__', problem['example_html'])
    html = html.replace('__TRACE_HTML__', problem['trace_html'])

    qt_opts = ''.join(f'<div class="quiz-opt rounded-lg px-3 py-2 text-sm mono" data-val="{o}">{o}</div>' for o in problem['quiz_time_opts'])
    qs_opts = ''.join(f'<div class="quiz-opt rounded-lg px-3 py-2 text-sm mono" data-val="{o}">{o}</div>' for o in problem['quiz_space_opts'])
    html = html.replace('__QUIZ_TIME_OPTIONS__', qt_opts)
    html = html.replace('__QUIZ_SPACE_OPTIONS__', qs_opts)
    html = html.replace('__QUIZ_TIME_CORRECT__', problem['time_big'])
    html = html.replace('__QUIZ_SPACE_CORRECT__', problem['space_big'])

    tricks_html = ''.join(f'<li>{t}</li>' for t in problem['tricks'])
    html = html.replace('__TRICKS_HTML__', tricks_html)

    html = html.replace('__APPROACH_HTML__', problem['approach_html'])
    html = html.replace('__PYTHON_CODE_HTML__', highlight_python(problem['python_code']))
    html = html.replace('__PYTHON_CODE_JS_STRING__', js_string(problem['python_code']))

    html = html.replace('__TIME_BIG__', problem['time_big'])
    html = html.replace('__TIME_EXPLAIN__', problem['time_explain'])
    html = html.replace('__SPACE_BIG__', problem['space_big'])
    html = html.replace('__SPACE_EXPLAIN__', problem['space_explain'])

    html = html.replace('__SIDEBAR_JSON__', json.dumps(problem['sidebar']))
    html = html.replace('__PREV_NEXT_HTML__', problem['prev_next_html'])
    html = html.replace('__TRACE_JS__', problem['trace_js'])

    return html

def prev_next(prev_slug, prev_title, next_slug, next_title):
    prev_html = f'''<a id="link-prev" href="./{prev_slug}" class="text-soft hover:accent-text transition flex items-center gap-2 text-sm font-semibold">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
          <span># {prev_title}</span>
        </a>''' if prev_slug else '''<span class="invisible"></span>'''
    next_html = f'''<a id="link-next" href="./{next_slug}" class="text-soft hover:accent-text transition flex items-center gap-2 text-sm font-semibold">
          <span># {next_title}</span>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
        </a>''' if next_slug else '''<span class="invisible"></span>'''
    return prev_html + '\n        ' + next_html

ARRAY_SIDEBAR = [
    {"slug": "two-sum", "title": "Two Sum", "implemented": True},
    {"slug": "container-with-most-water", "title": "Container With Most Water", "implemented": True},
    {"slug": "search-in-rotated-sorted-array", "title": "Search in Rotated Sorted Array", "implemented": True},
    {"slug": "maximum-subarray", "title": "Maximum Subarray", "implemented": True},
    {"slug": "longest-consecutive-sequence", "title": "Longest Consecutive Sequence", "implemented": True},
    {"slug": "maximum-product-subarray", "title": "Maximum Product Subarray", "implemented": True},
    {"slug": "find-minimum-in-rotated-sorted-array", "title": "Find Minimum in Rotated Sorted Array", "implemented": True},
    {"slug": "contains-duplicate", "title": "Contains Duplicate", "implemented": True},
    {"slug": "product-of-array-except-self", "title": "Product of Array Except Self", "implemented": False}
]
STRING_SIDEBAR = [
    {"slug": "group-anagrams", "title": "Group Anagrams", "implemented": True},
    {"slug": "longest-repeating-character-replacement", "title": "Longest Repeating Character Replacement", "implemented": True}
]
LINKED_LIST_SIDEBAR = [
    {"slug": "reverse-linked-list", "title": "Reverse Linked List", "implemented": True}
]

GENERIC_TRICKS = [
  '<strong class="accent-text">Count the loops, not the lines.</strong> One pass over n elements with O(1) work per element gives O(n); nested loops over the same input usually multiply.',
  '<strong class="accent-text">Hash set/map operations are O(1) average.</strong> A loop doing one lookup or insert per iteration stays O(n) overall — the hash structure doesn\'t add a factor.',
  '<strong class="accent-text">Space tracks "extra" memory, not the input.</strong> Ask what new structure you\'re building and how big it can get.',
  '<strong class="accent-text">Two pointers / sliding window ≠ O(n²).</strong> Even though it looks like nested loops, each pointer only ever moves forward — total work stays O(n).'
]

problems = []

# ---------- 1. container-with-most-water ----------
problems.append(dict(
    slug='container-with-most-water', title='Container With Most Water', category='Array',
    difficulty='Medium', tags=['Two Pointers', 'Array'],
    leetcode_url='https://leetcode.com/problems/container-with-most-water/',
    statement_html='''<p class="leading-relaxed mb-4">You are given an integer array <code class="mono px-1.5 py-0.5 rounded" style="background:var(--rail)">height</code> of length n. Two lines are drawn such that the two endpoints of line i are at <code class="mono px-1.5 py-0.5 rounded" style="background:var(--rail)">(i, 0)</code> and <code class="mono px-1.5 py-0.5 rounded" style="background:var(--rail)">(i, height[i])</code>. Find two lines that together with the x-axis form a container holding the most water.</p>
        <p class="text-soft text-sm mb-5">Return the maximum amount of water the container can store.</p>''',
    example_html='<p class="mb-1"><span class="text-soft">Input:</span> height = [1,8,6,2,5,4,8,3,7]</p><p><span class="text-soft">Output:</span> 49</p>',
    trace_html='<div id="array-track" class="flex gap-2 pb-7 pt-7 flex-wrap justify-center"></div>',
    quiz_time_opts=['O(1)', 'O(n)', 'O(n log n)', 'O(n²)'], quiz_space_opts=['O(1)', 'O(n)', 'O(log n)'],
    time_big='O(n)', time_explain='Two pointers move inward; each index is visited at most once.',
    space_big='O(1)', space_explain='Only two pointers and a running max are tracked — no extra structure.',
    tricks=GENERIC_TRICKS + ['<strong class="accent-text">Always move the shorter line.</strong> The container\'s height is capped by the shorter side, so keeping the taller one can never help — only moving the shorter pointer can find something better.'],
    approach_html='''<p class="mb-3">Start with the widest possible container — both ends of the array — and shrink inward. At each step, the area is capped by the <em>shorter</em> of the two lines, so moving the taller pointer can never increase the area. Always move the shorter one.</p>
        <ol class="list-decimal list-inside space-y-2 text-soft">
          <li>Place <code class="mono accent-text">left</code> at index 0 and <code class="mono accent-text">right</code> at the last index.</li>
          <li>Compute <code class="mono accent-text">area = (right - left) * min(height[left], height[right])</code> and track the max.</li>
          <li>Move whichever pointer points to the shorter line inward.</li>
          <li>Repeat until the pointers meet.</li>
        </ol>''',
    python_code='''from typing import List

class Solution:
    def maxArea(self, height: List[int]) -> int:
        left = 0
        right = len(height) - 1
        max_area = 0

        while left < right:
            width = right - left
            h = min(height[left], height[right])
            area = width * h
            max_area = max(max_area, area)

            if height[left] < height[right]:
                left += 1
            else:
                right -= 1

        return max_area''',
    sidebar=ARRAY_SIDEBAR,
    prev_next_html=prev_next('two-sum', 'Two Sum', 'search-in-rotated-sorted-array', 'Search in Rotated Sorted Array'),
    trace_js='''
    const HEIGHTS = [1, 8, 6, 2, 5, 4, 8, 3, 7];
    let steps = [], stepIndex = -1;

    function computeSteps() {
      steps = [];
      let left = 0, right = HEIGHTS.length - 1, maxArea = 0;
      while (left < right) {
        const width = right - left;
        const h = Math.min(HEIGHTS[left], HEIGHTS[right]);
        const area = width * h;
        const improved = area > maxArea;
        maxArea = Math.max(maxArea, area);
        steps.push({ left, right, area, maxArea, improved });
        if (HEIGHTS[left] < HEIGHTS[right]) left++; else right--;
      }
    }

    function buildTrace() {
      computeSteps(); stepIndex = -1;
      const track = document.getElementById('array-track');
      track.innerHTML = HEIGHTS.map((h, i) => `
        <div class="cell" id="cell-${i}" style="height:${28 + h * 6}px; align-items:flex-end; padding-bottom:6px;">${h}<span class="idx">i=${i}</span></div>`).join('');
      document.getElementById('trace-caption').textContent = 'Click "Next" to begin.';
      updateStepControls();
    }

    function renderStep() {
      HEIGHTS.forEach((_, i) => document.getElementById(`cell-${i}`).classList.remove('scan', 'hit', 'discarded'));
      const caption = document.getElementById('trace-caption');
      if (stepIndex < 0) { caption.textContent = 'Click "Next" to begin.'; updateStepControls(); return; }
      const s = steps[stepIndex];
      for (let i = 0; i < s.left; i++) document.getElementById(`cell-${i}`).classList.add('discarded');
      for (let i = s.right + 1; i < HEIGHTS.length; i++) document.getElementById(`cell-${i}`).classList.add('discarded');
      document.getElementById(`cell-${s.left}`).classList.add(s.improved ? 'hit' : 'scan');
      document.getElementById(`cell-${s.right}`).classList.add(s.improved ? 'hit' : 'scan');
      caption.textContent = `left=${s.left}, right=${s.right} → area=${s.area}${s.improved ? ' (new max!)' : ''} — running max: ${s.maxArea}`;
      updateStepControls();
    }

    function updateStepControls() {
      document.getElementById('step-counter').textContent = `Step ${stepIndex + 1} / ${steps.length}`;
      document.getElementById('btn-prev').disabled = stepIndex < 0;
      document.getElementById('btn-next').disabled = stepIndex >= steps.length - 1;
    }
'''
))

# ---------- 2. contains-duplicate ----------
problems.append(dict(
    slug='contains-duplicate', title='Contains Duplicate', category='Array',
    difficulty='Easy', tags=['Hash Set', 'Array'],
    leetcode_url='https://leetcode.com/problems/contains-duplicate/',
    statement_html='''<p class="leading-relaxed mb-4">Given an integer array <code class="mono px-1.5 py-0.5 rounded" style="background:var(--rail)">nums</code>, return <code class="mono px-1.5 py-0.5 rounded" style="background:var(--rail)">true</code> if any value appears at least twice, and <code class="mono px-1.5 py-0.5 rounded" style="background:var(--rail)">false</code> if every element is distinct.</p>''',
    example_html='<p class="mb-1"><span class="text-soft">Input:</span> nums = [1,2,3,1]</p><p><span class="text-soft">Output:</span> true</p>',
    trace_html='''<div id="array-track" class="flex gap-3 pb-5"></div>
          <div class="w-full"><p class="text-xs font-bold uppercase tracking-wider text-soft mb-2">hash set &nbsp;(seen so far)</p>
          <div id="map-track" class="flex gap-2 flex-wrap min-h-[42px]"></div></div>''',
    quiz_time_opts=['O(1)', 'O(n)', 'O(n log n)', 'O(n²)'], quiz_space_opts=['O(1)', 'O(n)', 'O(log n)'],
    time_big='O(n)', time_explain='Single pass; each hash set lookup/insert is O(1) average.',
    space_big='O(n)', space_explain='In the worst case (no duplicates) the set holds all n elements.',
    tricks=GENERIC_TRICKS,
    approach_html='''<p class="mb-3">Walk the array once, tracking every value you\'ve already seen in a hash set. The moment you encounter a value already in the set, you\'ve found a duplicate.</p>
        <ol class="list-decimal list-inside space-y-2 text-soft">
          <li>For each number, check if it\'s already in <code class="mono accent-text">seen</code>.</li>
          <li>If it is, return <code class="mono accent-text">True</code> immediately.</li>
          <li>Otherwise, add it to <code class="mono accent-text">seen</code> and continue.</li>
          <li>If the loop finishes without a hit, return <code class="mono accent-text">False</code>.</li>
        </ol>''',
    python_code='''from typing import List

class Solution:
    def containsDuplicate(self, nums: List[int]) -> bool:
        seen = set()

        for num in nums:
            if num in seen:
                return True
            seen.add(num)

        return False''',
    sidebar=ARRAY_SIDEBAR,
    prev_next_html=prev_next('find-minimum-in-rotated-sorted-array', 'Find Minimum in Rotated Sorted Array', None, None),
    trace_js='''
    const NUMS = [1, 2, 3, 1];
    let steps = [], stepIndex = -1;

    function computeSteps() {
      steps = [];
      const seen = new Set();
      for (let i = 0; i < NUMS.length; i++) {
        const isDup = seen.has(NUMS[i]);
        steps.push({ i, isDup, snapshot: new Set(seen) });
        if (isDup) break;
        seen.add(NUMS[i]);
      }
    }

    function buildTrace() {
      computeSteps(); stepIndex = -1;
      const track = document.getElementById('array-track');
      track.innerHTML = NUMS.map((n, i) => `<div class="cell" id="cell-${i}">${n}<span class="idx">i=${i}</span></div>`).join('');
      document.getElementById('map-track').innerHTML = '';
      document.getElementById('trace-caption').textContent = 'Click "Next" to begin.';
      updateStepControls();
    }

    function renderStep() {
      NUMS.forEach((_, i) => document.getElementById(`cell-${i}`).classList.remove('scan', 'hit', 'done'));
      const mapTrack = document.getElementById('map-track');
      const caption = document.getElementById('trace-caption');
      if (stepIndex < 0) { mapTrack.innerHTML = ''; caption.textContent = 'Click "Next" to begin.'; updateStepControls(); return; }
      const s = steps[stepIndex];
      mapTrack.innerHTML = Array.from(s.snapshot).map(v => `<div class="map-slot filled">${v}</div>`).join('') || '<span class="text-xs text-soft mono">empty</span>';
      for (let i = 0; i < s.i; i++) document.getElementById(`cell-${i}`).classList.add('done');
      document.getElementById(`cell-${s.i}`).classList.add(s.isDup ? 'hit' : 'scan');
      caption.textContent = s.isDup
        ? `nums[${s.i}]=${NUMS[s.i]} was already seen → return True`
        : `nums[${s.i}]=${NUMS[s.i]} is new → add to set`;
      updateStepControls();
    }

    function updateStepControls() {
      document.getElementById('step-counter').textContent = `Step ${stepIndex + 1} / ${steps.length}`;
      document.getElementById('btn-prev').disabled = stepIndex < 0;
      document.getElementById('btn-next').disabled = stepIndex >= steps.length - 1;
    }
'''
))

# ---------- 3. find-minimum-in-rotated-sorted-array ----------
problems.append(dict(
    slug='find-minimum-in-rotated-sorted-array', title='Find Minimum in Rotated Sorted Array', category='Array',
    difficulty='Medium', tags=['Binary Search', 'Array'],
    leetcode_url='https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/',
    statement_html='''<p class="leading-relaxed mb-4">A sorted array of unique elements was rotated at an unknown pivot. Given the rotated array <code class="mono px-1.5 py-0.5 rounded" style="background:var(--rail)">nums</code>, return the minimum element.</p>
        <p class="text-soft text-sm mb-5">You must write an algorithm that runs in <span class="mono accent-text">O(log n)</span> time.</p>''',
    example_html='<p class="mb-1"><span class="text-soft">Input:</span> nums = [3,4,5,1,2]</p><p><span class="text-soft">Output:</span> 1</p>',
    trace_html='<div id="array-track" class="flex gap-3 pb-7 pt-7"></div>',
    quiz_time_opts=['O(1)', 'O(log n)', 'O(n)', 'O(n log n)'], quiz_space_opts=['O(1)', 'O(n)', 'O(log n)'],
    time_big='O(log n)', time_explain='The search window halves on every iteration of binary search.',
    space_big='O(1)', space_explain='Only two or three index pointers are tracked.',
    tricks=GENERIC_TRICKS + ['<strong class="accent-text">Compare against the right boundary, not the left.</strong> If <code class="mono">nums[mid] &gt; nums[right]</code>, the minimum must be to the right of mid; otherwise it\'s at mid or to the left — this single comparison drives the whole search.'],
    approach_html='''<p class="mb-3">The minimum is the one point where the "rotation break" happens. Binary search by comparing the middle element to the rightmost element: if mid is greater than the right end, the break (and the minimum) is to the right; otherwise it\'s at or before mid.</p>
        <ol class="list-decimal list-inside space-y-2 text-soft">
          <li>Set <code class="mono accent-text">left = 0</code>, <code class="mono accent-text">right = len(nums) - 1</code>.</li>
          <li>While <code class="mono accent-text">left &lt; right</code>, compute <code class="mono accent-text">mid</code>.</li>
          <li>If <code class="mono accent-text">nums[mid] &gt; nums[right]</code>, the minimum is past mid → <code class="mono accent-text">left = mid + 1</code>.</li>
          <li>Otherwise the minimum is at or before mid → <code class="mono accent-text">right = mid</code>.</li>
          <li>When the loop ends, <code class="mono accent-text">left == right</code> points at the minimum.</li>
        </ol>''',
    python_code='''from typing import List

class Solution:
    def findMin(self, nums: List[int]) -> int:
        left, right = 0, len(nums) - 1

        while left < right:
            mid = (left + right) // 2

            if nums[mid] > nums[right]:
                left = mid + 1
            else:
                right = mid

        return nums[left]''',
    sidebar=ARRAY_SIDEBAR,
    prev_next_html=prev_next('maximum-product-subarray', 'Maximum Product Subarray', 'contains-duplicate', 'Contains Duplicate'),
    trace_js='''
    const NUMS = [3, 4, 5, 1, 2];
    let steps = [], stepIndex = -1;

    function computeSteps() {
      steps = [];
      let left = 0, right = NUMS.length - 1;
      while (left < right) {
        const mid = Math.floor((left + right) / 2);
        const goRight = NUMS[mid] > NUMS[right];
        steps.push({ left, mid, right, goRight });
        if (goRight) left = mid + 1; else right = mid;
      }
      steps.push({ left, mid: left, right: left, final: true });
    }

    function buildTrace() {
      computeSteps(); stepIndex = -1;
      const track = document.getElementById('array-track');
      track.innerHTML = NUMS.map((n, i) => `<div class="cell" id="cell-${i}">${n}<span class="idx">i=${i}</span><span class="ptr" id="ptr-${i}"></span></div>`).join('');
      document.getElementById('trace-caption').textContent = 'Click "Next" to begin.';
      updateStepControls();
    }

    function setPointers(left, mid, right) {
      NUMS.forEach((_, i) => {
        const p = document.getElementById(`ptr-${i}`);
        let labels = [];
        if (i === left) labels.push('L');
        if (i === mid) labels.push('M');
        if (i === right) labels.push('R');
        p.textContent = labels.join('/');
        p.style.opacity = labels.length ? 1 : 0;
      });
    }

    function renderStep() {
      const caption = document.getElementById('trace-caption');
      if (stepIndex < 0) {
        NUMS.forEach((_, i) => { document.getElementById(`cell-${i}`).classList.remove('discarded', 'scan', 'hit'); document.getElementById(`ptr-${i}`).style.opacity = 0; });
        caption.textContent = 'Click "Next" to begin.'; updateStepControls(); return;
      }
      const s = steps[stepIndex];
      NUMS.forEach((_, i) => {
        document.getElementById(`cell-${i}`).classList.toggle('discarded', i < s.left || i > s.right);
        document.getElementById(`cell-${i}`).classList.remove('scan', 'hit');
      });
      setPointers(s.left, s.mid, s.right);
      if (s.final) {
        document.getElementById(`cell-${s.left}`).classList.add('hit');
        caption.textContent = `left == right → minimum found: nums[${s.left}] = ${NUMS[s.left]}`;
      } else {
        document.getElementById(`cell-${s.mid}`).classList.add('scan');
        caption.textContent = `mid=${s.mid} → nums[mid]=${NUMS[s.mid]} ${s.goRight ? '>' : '<='} nums[right]=${NUMS[s.right]} → search ${s.goRight ? 'right' : 'left'} half`;
      }
      updateStepControls();
    }

    function updateStepControls() {
      document.getElementById('step-counter').textContent = `Step ${stepIndex + 1} / ${steps.length}`;
      document.getElementById('btn-prev').disabled = stepIndex < 0;
      document.getElementById('btn-next').disabled = stepIndex >= steps.length - 1;
    }
'''
))

# ---------- 4. group-anagrams ----------
problems.append(dict(
    slug='group-anagrams', title='Group Anagrams', category='String',
    difficulty='Medium', tags=['Hash Map', 'String'],
    leetcode_url='https://leetcode.com/problems/group-anagrams/',
    statement_html='''<p class="leading-relaxed mb-4">Given an array of strings <code class="mono px-1.5 py-0.5 rounded" style="background:var(--rail)">strs</code>, group the anagrams together. Two strings are anagrams if one can be rearranged to form the other.</p>''',
    example_html='<p class="mb-1"><span class="text-soft">Input:</span> strs = ["eat","tea","tan","ate","nat","bat"]</p><p><span class="text-soft">Output:</span> [["eat","tea","ate"],["tan","nat"],["bat"]]</p>',
    trace_html='''<div id="array-track" class="flex gap-3 pb-5 flex-wrap justify-center"></div>
          <div class="w-full"><p class="text-xs font-bold uppercase tracking-wider text-soft mb-2">groups &nbsp;(sorted key → words)</p>
          <div id="map-track" class="flex flex-col gap-2 min-h-[42px] w-full"></div></div>''',
    quiz_time_opts=['O(n)', 'O(n·k log k)', 'O(n²)', 'O(n log n)'], quiz_space_opts=['O(1)', 'O(n·k)', 'O(log n)'],
    time_big='O(n·k log k)', time_explain='n strings, each sorted in O(k log k) where k is the max string length.',
    space_big='O(n·k)', space_explain='The map stores every input string across all groups.',
    tricks=GENERIC_TRICKS + ['<strong class="accent-text">A sorted string is a perfect anagram fingerprint.</strong> Any two anagrams collapse to the exact same sorted key, so a hash map keyed on that string groups them in one pass.'],
    approach_html='''<p class="mb-3">Anagrams share the same letters, just in different orders — so sorting each string\'s letters gives a canonical key that\'s identical for every anagram in a group. Use that sorted string as a hash map key.</p>
        <ol class="list-decimal list-inside space-y-2 text-soft">
          <li>For each word, compute <code class="mono accent-text">key = sorted(word)</code>.</li>
          <li>Append the original word to <code class="mono accent-text">groups[key]</code>.</li>
          <li>After processing every word, return all the map\'s values as the grouped lists.</li>
        </ol>''',
    python_code='''from typing import List
from collections import defaultdict

class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        groups = defaultdict(list)

        for s in strs:
            key = ''.join(sorted(s))
            groups[key].append(s)

        return list(groups.values())''',
    sidebar=STRING_SIDEBAR,
    prev_next_html=prev_next(None, None, 'longest-repeating-character-replacement', 'Longest Repeating Character Replacement'),
    trace_js='''
    const WORDS = ["eat", "tea", "tan", "ate", "nat", "bat"];
    function sortedKey(w) { return w.split('').sort().join(''); }
    let steps = [], stepIndex = -1;

    function computeSteps() {
      steps = [];
      const groups = new Map();
      for (let i = 0; i < WORDS.length; i++) {
        const key = sortedKey(WORDS[i]);
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push(WORDS[i]);
        steps.push({ i, key, snapshot: new Map([...groups].map(([k, v]) => [k, [...v]])) });
      }
    }

    function buildTrace() {
      computeSteps(); stepIndex = -1;
      const track = document.getElementById('array-track');
      track.innerHTML = WORDS.map((w, i) => `<div class="cell" id="cell-${i}" style="min-width:64px;">${w}<span class="idx">i=${i}</span></div>`).join('');
      document.getElementById('map-track').innerHTML = '';
      document.getElementById('trace-caption').textContent = 'Click "Next" to begin.';
      updateStepControls();
    }

    function renderStep() {
      WORDS.forEach((_, i) => document.getElementById(`cell-${i}`).classList.remove('scan', 'hit', 'done'));
      const mapTrack = document.getElementById('map-track');
      const caption = document.getElementById('trace-caption');
      if (stepIndex < 0) { mapTrack.innerHTML = ''; caption.textContent = 'Click "Next" to begin.'; updateStepControls(); return; }
      const s = steps[stepIndex];
      mapTrack.innerHTML = Array.from(s.snapshot.entries()).map(([k, words]) =>
        `<div class="map-slot filled" style="display:flex; gap:6px; align-items:center;"><span class="text-soft">"${k}"</span> → [${words.join(', ')}]</div>`
      ).join('');
      for (let i = 0; i < s.i; i++) document.getElementById(`cell-${i}`).classList.add('done');
      document.getElementById(`cell-${s.i}`).classList.add('scan');
      caption.textContent = `"${WORDS[s.i]}" → sorted key "${s.key}" → append to that group`;
      updateStepControls();
    }

    function updateStepControls() {
      document.getElementById('step-counter').textContent = `Step ${stepIndex + 1} / ${steps.length}`;
      document.getElementById('btn-prev').disabled = stepIndex < 0;
      document.getElementById('btn-next').disabled = stepIndex >= steps.length - 1;
    }
'''
))

# ---------- 5. longest-consecutive-sequence ----------
problems.append(dict(
    slug='longest-consecutive-sequence', title='Longest Consecutive Sequence', category='Array',
    difficulty='Medium', tags=['Hash Set', 'Array'],
    leetcode_url='https://leetcode.com/problems/longest-consecutive-sequence/',
    statement_html='''<p class="leading-relaxed mb-4">Given an unsorted array of integers <code class="mono px-1.5 py-0.5 rounded" style="background:var(--rail)">nums</code>, return the length of the longest consecutive elements sequence.</p>
        <p class="text-soft text-sm mb-5">You must write an algorithm that runs in <span class="mono accent-text">O(n)</span> time.</p>''',
    example_html='<p class="mb-1"><span class="text-soft">Input:</span> nums = [100,4,200,1,3,2]</p><p><span class="text-soft">Output:</span> 4 <span class="cm">// the sequence [1,2,3,4]</span></p>',
    trace_html='<div id="array-track" class="flex gap-2 pb-7 pt-7 flex-wrap justify-center"></div>',
    quiz_time_opts=['O(n)', 'O(n log n)', 'O(n²)', 'O(1)'], quiz_space_opts=['O(1)', 'O(n)', 'O(log n)'],
    time_big='O(n)', time_explain='Each number is only ever extended into a chain once, despite the nested-looking loop.',
    space_big='O(n)', space_explain='The hash set stores every distinct number.',
    tricks=GENERIC_TRICKS + ['<strong class="accent-text">Only start counting from a true chain start.</strong> By skipping any number whose predecessor exists in the set, each chain is walked exactly once in total — that\'s what keeps this O(n) instead of O(n²).'],
    approach_html='''<p class="mb-3">Put every number in a hash set for O(1) lookups. For each number, only start counting a sequence if it\'s a true "chain start" — meaning <code class="mono accent-text">num - 1</code> is NOT in the set. From there, count forward as long as consecutive numbers exist.</p>
        <ol class="list-decimal list-inside space-y-2 text-soft">
          <li>Build a set of all numbers for O(1) membership checks.</li>
          <li>For each number, skip it unless it\'s a chain start (<code class="mono accent-text">num - 1</code> not in set).</li>
          <li>From a chain start, keep extending forward (<code class="mono accent-text">num + 1</code>, <code class="mono accent-text">num + 2</code>, …) while present in the set.</li>
          <li>Track the longest chain length seen.</li>
        </ol>''',
    python_code='''from typing import List

class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        num_set = set(nums)
        longest = 0

        for num in num_set:
            if num - 1 not in num_set:
                length = 1
                while num + length in num_set:
                    length += 1
                longest = max(longest, length)

        return longest''',
    sidebar=ARRAY_SIDEBAR,
    prev_next_html=prev_next('search-in-rotated-sorted-array', 'Search in Rotated Sorted Array', 'maximum-product-subarray', 'Maximum Product Subarray'),
    trace_js='''
    const NUMS = [100, 4, 200, 1, 3, 2];
    let steps = [], stepIndex = -1;

    function computeSteps() {
      steps = [];
      const set = new Set(NUMS);
      let longest = 0;
      for (const num of new Set(NUMS)) {
        const isStart = !set.has(num - 1);
        if (!isStart) { steps.push({ num, isStart, longest }); continue; }
        let length = 1;
        const chain = [num];
        while (set.has(num + length)) { chain.push(num + length); length++; }
        longest = Math.max(longest, length);
        steps.push({ num, isStart, length, chain, longest });
      }
    }

    function buildTrace() {
      computeSteps(); stepIndex = -1;
      const track = document.getElementById('array-track');
      track.innerHTML = NUMS.map((n, i) => `<div class="cell" id="cell-${i}">${n}<span class="idx">i=${i}</span></div>`).join('');
      document.getElementById('trace-caption').textContent = 'Click "Next" to begin.';
      updateStepControls();
    }

    function renderStep() {
      NUMS.forEach((_, i) => document.getElementById(`cell-${i}`).classList.remove('scan', 'hit'));
      const caption = document.getElementById('trace-caption');
      if (stepIndex < 0) { caption.textContent = 'Click "Next" to begin.'; updateStepControls(); return; }
      const s = steps[stepIndex];
      if (!s.isStart) {
        const idx = NUMS.indexOf(s.num);
        document.getElementById(`cell-${idx}`).classList.add('scan');
        caption.textContent = `${s.num} - 1 = ${s.num - 1} is in the set → not a chain start, skip`;
      } else {
        s.chain.forEach(v => { const idx = NUMS.indexOf(v); if (idx !== -1) document.getElementById(`cell-${idx}`).classList.add('hit'); });
        caption.textContent = `${s.num} is a chain start → chain [${s.chain.join(',')}] length=${s.length} — longest so far: ${s.longest}`;
      }
      updateStepControls();
    }

    function updateStepControls() {
      document.getElementById('step-counter').textContent = `Step ${stepIndex + 1} / ${steps.length}`;
      document.getElementById('btn-prev').disabled = stepIndex < 0;
      document.getElementById('btn-next').disabled = stepIndex >= steps.length - 1;
    }
'''
))

# ---------- 6. longest-repeating-character-replacement ----------
problems.append(dict(
    slug='longest-repeating-character-replacement', title='Longest Repeating Character Replacement', category='String',
    difficulty='Medium', tags=['Sliding Window', 'String'],
    leetcode_url='https://leetcode.com/problems/longest-repeating-character-replacement/',
    statement_html='''<p class="leading-relaxed mb-4">Given a string <code class="mono px-1.5 py-0.5 rounded" style="background:var(--rail)">s</code> and an integer <code class="mono px-1.5 py-0.5 rounded" style="background:var(--rail)">k</code>, you can replace up to <code class="mono px-1.5 py-0.5 rounded" style="background:var(--rail)">k</code> characters with any other character. Return the length of the longest substring containing the same letter after the replacements.</p>''',
    example_html='<p class="mb-1"><span class="text-soft">Input:</span> s = "AABABBA", k = 1</p><p><span class="text-soft">Output:</span> 4</p>',
    trace_html='<div id="array-track" class="flex gap-2 pb-7 pt-7 flex-wrap justify-center"></div>',
    quiz_time_opts=['O(1)', 'O(n)', 'O(n log n)', 'O(n²)'], quiz_space_opts=['O(1)', 'O(n)', 'O(26)'],
    time_big='O(n)', time_explain='A sliding window where both pointers only ever move forward — total O(n) work.',
    space_big='O(1)', space_explain='The frequency map holds at most 26 letters — constant regardless of n.',
    tricks=GENERIC_TRICKS + ['<strong class="accent-text">"Window length minus max frequency" is the replacement cost.</strong> If that exceeds k, the window is invalid — shrink from the left instead of resetting it.'],
    approach_html='''<p class="mb-3">Maintain a sliding window and a frequency count of letters inside it. A window is valid if <code class="mono accent-text">(window length − count of the most frequent letter) ≤ k</code> — that difference is exactly how many characters you\'d need to replace. Expand the window each step; shrink from the left only when it becomes invalid.</p>
        <ol class="list-decimal list-inside space-y-2 text-soft">
          <li>Expand <code class="mono accent-text">right</code> one character at a time, updating the frequency count.</li>
          <li>Track <code class="mono accent-text">max_freq</code>, the count of the most common letter currently in the window.</li>
          <li>If <code class="mono accent-text">window_len - max_freq &gt; k</code>, shrink from <code class="mono accent-text">left</code>.</li>
          <li>Track the largest valid window length seen.</li>
        </ol>''',
    python_code='''class Solution:
    def characterReplacement(self, s: str, k: int) -> int:
        count = {}
        left = 0
        max_freq = 0
        result = 0

        for right in range(len(s)):
            count[s[right]] = count.get(s[right], 0) + 1
            max_freq = max(max_freq, count[s[right]])

            window_len = right - left + 1
            if window_len - max_freq > k:
                count[s[left]] -= 1
                left += 1

            result = max(result, right - left + 1)

        return result''',
    sidebar=STRING_SIDEBAR,
    prev_next_html=prev_next('group-anagrams', 'Group Anagrams', None, None),
    trace_js='''
    const S = "AABABBA";
    const K = 1;
    let steps = [], stepIndex = -1;

    function computeSteps() {
      steps = [];
      const count = {};
      let left = 0, maxFreq = 0, result = 0;
      for (let right = 0; right < S.length; right++) {
        count[S[right]] = (count[S[right]] || 0) + 1;
        maxFreq = Math.max(maxFreq, count[S[right]]);
        const windowLen = right - left + 1;
        let shrunk = false;
        if (windowLen - maxFreq > K) {
          count[S[left]]--; left++; shrunk = true;
        }
        result = Math.max(result, right - left + 1);
        steps.push({ left, right, maxFreq, result, shrunk });
      }
    }

    function buildTrace() {
      computeSteps(); stepIndex = -1;
      const track = document.getElementById('array-track');
      track.innerHTML = S.split('').map((ch, i) => `<div class="cell" id="cell-${i}">${ch}<span class="idx">i=${i}</span></div>`).join('');
      document.getElementById('trace-caption').textContent = 'Click "Next" to begin.';
      updateStepControls();
    }

    function renderStep() {
      S.split('').forEach((_, i) => document.getElementById(`cell-${i}`).classList.remove('scan', 'hit', 'discarded'));
      const caption = document.getElementById('trace-caption');
      if (stepIndex < 0) { caption.textContent = 'Click "Next" to begin.'; updateStepControls(); return; }
      const s = steps[stepIndex];
      for (let i = 0; i < s.left; i++) document.getElementById(`cell-${i}`).classList.add('discarded');
      for (let i = s.left; i <= s.right; i++) document.getElementById(`cell-${i}`).classList.add('hit');
      caption.textContent = `window [${s.left},${s.right}] maxFreq=${s.maxFreq}${s.shrunk ? ' — too many replacements needed, shrank left' : ''} — best length so far: ${s.result}`;
      updateStepControls();
    }

    function updateStepControls() {
      document.getElementById('step-counter').textContent = `Step ${stepIndex + 1} / ${steps.length}`;
      document.getElementById('btn-prev').disabled = stepIndex < 0;
      document.getElementById('btn-next').disabled = stepIndex >= steps.length - 1;
    }
'''
))

# ---------- 7. maximum-product-subarray ----------
problems.append(dict(
    slug='maximum-product-subarray', title='Maximum Product Subarray', category='Array',
    difficulty='Medium', tags=['Dynamic Programming', 'Array'],
    leetcode_url='https://leetcode.com/problems/maximum-product-subarray/',
    statement_html='''<p class="leading-relaxed mb-4">Given an integer array <code class="mono px-1.5 py-0.5 rounded" style="background:var(--rail)">nums</code>, find a contiguous non-empty subarray with the largest product, and return that product.</p>''',
    example_html='<p class="mb-1"><span class="text-soft">Input:</span> nums = [2,3,-2,4]</p><p><span class="text-soft">Output:</span> 6 <span class="cm">// [2,3] has the largest product</span></p>',
    trace_html='<div id="array-track" class="flex gap-3 pb-7 pt-7"></div>',
    quiz_time_opts=['O(1)', 'O(n)', 'O(n log n)', 'O(n²)'], quiz_space_opts=['O(1)', 'O(n)', 'O(log n)'],
    time_big='O(n)', time_explain='A single pass, tracking running max and min in constant time per step.',
    space_big='O(1)', space_explain='Only a few running variables are kept — no array or map.',
    tricks=GENERIC_TRICKS + ['<strong class="accent-text">Track both a running max AND min.</strong> A negative number can flip the smallest product into the largest — so you need the running minimum too, not just the maximum, in case the next number is negative.'],
    approach_html='''<p class="mb-3">Unlike maximum <em>sum</em> subarray, products are tricky because a negative number can turn a very small (negative) product into the largest one. So track both a running max and a running min at every index — either could become the new max once multiplied by a negative number.</p>
        <ol class="list-decimal list-inside space-y-2 text-soft">
          <li>Initialize <code class="mono accent-text">cur_max</code> and <code class="mono accent-text">cur_min</code> to the first element.</li>
          <li>At each new number, compute candidates: the number itself, <code class="mono accent-text">cur_max * num</code>, and <code class="mono accent-text">cur_min * num</code>.</li>
          <li>The new <code class="mono accent-text">cur_max</code>/<code class="mono accent-text">cur_min</code> are the max/min of those three candidates.</li>
          <li>Update the global result with <code class="mono accent-text">cur_max</code> at every step.</li>
        </ol>''',
    python_code='''from typing import List

class Solution:
    def maxProduct(self, nums: List[int]) -> int:
        result = nums[0]
        cur_max, cur_min = nums[0], nums[0]

        for num in nums[1:]:
            candidates = (num, cur_max * num, cur_min * num)
            cur_max, cur_min = max(candidates), min(candidates)
            result = max(result, cur_max)

        return result''',
    sidebar=ARRAY_SIDEBAR,
    prev_next_html=prev_next('longest-consecutive-sequence', 'Longest Consecutive Sequence', 'find-minimum-in-rotated-sorted-array', 'Find Minimum in Rotated Sorted Array'),
    trace_js='''
    const NUMS = [2, 3, -2, 4];
    let steps = [], stepIndex = -1;

    function computeSteps() {
      steps = [];
      let result = NUMS[0], curMax = NUMS[0], curMin = NUMS[0];
      steps.push({ i: 0, curMax, curMin, result });
      for (let i = 1; i < NUMS.length; i++) {
        const num = NUMS[i];
        const candidates = [num, curMax * num, curMin * num];
        curMax = Math.max(...candidates);
        curMin = Math.min(...candidates);
        result = Math.max(result, curMax);
        steps.push({ i, curMax, curMin, result });
      }
    }

    function buildTrace() {
      computeSteps(); stepIndex = -1;
      const track = document.getElementById('array-track');
      track.innerHTML = NUMS.map((n, i) => `<div class="cell" id="cell-${i}">${n}<span class="idx">i=${i}</span></div>`).join('');
      document.getElementById('trace-caption').textContent = 'Click "Next" to begin.';
      updateStepControls();
    }

    function renderStep() {
      NUMS.forEach((_, i) => document.getElementById(`cell-${i}`).classList.remove('scan', 'hit', 'done'));
      const caption = document.getElementById('trace-caption');
      if (stepIndex < 0) { caption.textContent = 'Click "Next" to begin.'; updateStepControls(); return; }
      const s = steps[stepIndex];
      for (let i = 0; i < s.i; i++) document.getElementById(`cell-${i}`).classList.add('done');
      document.getElementById(`cell-${s.i}`).classList.add('scan');
      caption.textContent = `i=${s.i} → curMax=${s.curMax}, curMin=${s.curMin}, best so far=${s.result}`;
      updateStepControls();
    }

    function updateStepControls() {
      document.getElementById('step-counter').textContent = `Step ${stepIndex + 1} / ${steps.length}`;
      document.getElementById('btn-prev').disabled = stepIndex < 0;
      document.getElementById('btn-next').disabled = stepIndex >= steps.length - 1;
    }
'''
))

# ---------- 8. maximum-subarray ----------
problems.append(dict(
    slug='maximum-subarray', title='Maximum Subarray', category='Array',
    difficulty='Medium', tags=['Dynamic Programming', 'Array'],
    leetcode_url='https://leetcode.com/problems/maximum-subarray/',
    statement_html='''<p class="leading-relaxed mb-4">Given an integer array <code class="mono px-1.5 py-0.5 rounded" style="background:var(--rail)">nums</code>, find the contiguous subarray (containing at least one number) with the largest sum, and return its sum.</p>''',
    example_html='<p class="mb-1"><span class="text-soft">Input:</span> nums = [-2,1,-3,4,-1,2,1,-5,4]</p><p><span class="text-soft">Output:</span> 6 <span class="cm">// [4,-1,2,1] has the largest sum</span></p>',
    trace_html='<div id="array-track" class="flex gap-3 pb-7 pt-7"></div>',
    quiz_time_opts=['O(1)', 'O(n)', 'O(n log n)', 'O(n²)'], quiz_space_opts=['O(1)', 'O(n)', 'O(log n)'],
    time_big='O(n)', time_explain="Kadane's algorithm makes a single pass, doing constant work per element.",
    space_big='O(1)', space_explain='Only two running variables are tracked: the current sum and the best sum.',
    tricks=GENERIC_TRICKS + ['<strong class="accent-text">"Extend or restart" is the whole trick.</strong> At each element, ask: does adding this to my current run help, or would I be better off starting fresh from here? That single decision is Kadane\'s algorithm.'],
    approach_html='''<p class="mb-3">This is the classic <strong>Kadane\'s algorithm</strong>. At each index, decide whether to extend the current running subarray or start a brand-new one from the current element — whichever gives a larger sum.</p>
        <ol class="list-decimal list-inside space-y-2 text-soft">
          <li>Initialize <code class="mono accent-text">current_sum</code> and <code class="mono accent-text">max_sum</code> to the first element.</li>
          <li>For each next number, set <code class="mono accent-text">current_sum = max(num, current_sum + num)</code>.</li>
          <li>Update <code class="mono accent-text">max_sum = max(max_sum, current_sum)</code>.</li>
          <li>Return <code class="mono accent-text">max_sum</code> after the pass.</li>
        </ol>''',
    python_code='''from typing import List

class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        max_sum = nums[0]
        current_sum = nums[0]

        for num in nums[1:]:
            current_sum = max(num, current_sum + num)
            max_sum = max(max_sum, current_sum)

        return max_sum''',
    sidebar=ARRAY_SIDEBAR,
    prev_next_html=prev_next('container-with-most-water', 'Container With Most Water', 'longest-consecutive-sequence', 'Longest Consecutive Sequence'),
    trace_js='''
    const NUMS = [-2, 1, -3, 4, -1, 2, 1, -5, 4];
    let steps = [], stepIndex = -1;

    function computeSteps() {
      steps = [];
      let maxSum = NUMS[0], curSum = NUMS[0];
      steps.push({ i: 0, curSum, maxSum, restarted: false });
      for (let i = 1; i < NUMS.length; i++) {
        const num = NUMS[i];
        const restarted = num > curSum + num;
        curSum = Math.max(num, curSum + num);
        maxSum = Math.max(maxSum, curSum);
        steps.push({ i, curSum, maxSum, restarted });
      }
    }

    function buildTrace() {
      computeSteps(); stepIndex = -1;
      const track = document.getElementById('array-track');
      track.innerHTML = NUMS.map((n, i) => `<div class="cell" id="cell-${i}">${n}<span class="idx">i=${i}</span></div>`).join('');
      document.getElementById('trace-caption').textContent = 'Click "Next" to begin.';
      updateStepControls();
    }

    function renderStep() {
      NUMS.forEach((_, i) => document.getElementById(`cell-${i}`).classList.remove('scan', 'hit', 'done'));
      const caption = document.getElementById('trace-caption');
      if (stepIndex < 0) { caption.textContent = 'Click "Next" to begin.'; updateStepControls(); return; }
      const s = steps[stepIndex];
      for (let i = 0; i < s.i; i++) document.getElementById(`cell-${i}`).classList.add('done');
      document.getElementById(`cell-${s.i}`).classList.add(s.curSum === s.maxSum ? 'hit' : 'scan');
      caption.textContent = `i=${s.i} → ${s.restarted ? 'restarted run here' : 'extended the run'} → current_sum=${s.curSum}, max_sum=${s.maxSum}`;
      updateStepControls();
    }

    function updateStepControls() {
      document.getElementById('step-counter').textContent = `Step ${stepIndex + 1} / ${steps.length}`;
      document.getElementById('btn-prev').disabled = stepIndex < 0;
      document.getElementById('btn-next').disabled = stepIndex >= steps.length - 1;
    }
'''
))

# ---------- 9. reverse-linked-list ----------
problems.append(dict(
    slug='reverse-linked-list', title='Reverse Linked List', category='Linked List',
    difficulty='Easy', tags=['Linked List', 'Pointers'],
    leetcode_url='https://leetcode.com/problems/reverse-linked-list/',
    statement_html='''<p class="leading-relaxed mb-4">Given the <code class="mono px-1.5 py-0.5 rounded" style="background:var(--rail)">head</code> of a singly linked list, reverse the list and return the new head.</p>''',
    example_html='<p class="mb-1"><span class="text-soft">Input:</span> head = [1,2,3,4,5]</p><p><span class="text-soft">Output:</span> [5,4,3,2,1]</p>',
    trace_html='<div id="array-track" class="flex gap-2 pb-7 pt-7 flex-wrap justify-center items-center"></div>',
    quiz_time_opts=['O(1)', 'O(n)', 'O(n log n)', 'O(n²)'], quiz_space_opts=['O(1)', 'O(n)', 'O(log n)'],
    time_big='O(n)', time_explain='Every node is visited exactly once to flip its pointer.',
    space_big='O(1)', space_explain='Only two or three pointers are tracked — the list is reversed in place.',
    tricks=GENERIC_TRICKS[:3] + ['<strong class="accent-text">Save next before you overwrite it.</strong> The single most common bug in pointer-reversal problems is losing the rest of the list because you flipped <code class="mono">curr.next</code> before storing where it pointed.'],
    approach_html='''<p class="mb-3">Walk the list once, flipping each node\'s <code class="mono accent-text">next</code> pointer to point backward instead of forward. Three pointers do the work: <code class="mono accent-text">prev</code> (the reversed portion so far), <code class="mono accent-text">curr</code> (the node being flipped), and a temporary <code class="mono accent-text">next_node</code> to avoid losing the rest of the list.</p>
        <ol class="list-decimal list-inside space-y-2 text-soft">
          <li>Start with <code class="mono accent-text">prev = None</code>, <code class="mono accent-text">curr = head</code>.</li>
          <li>Save <code class="mono accent-text">next_node = curr.next</code> before changing anything.</li>
          <li>Flip the pointer: <code class="mono accent-text">curr.next = prev</code>.</li>
          <li>Advance both: <code class="mono accent-text">prev = curr</code>, <code class="mono accent-text">curr = next_node</code>.</li>
          <li>When <code class="mono accent-text">curr</code> is <code class="mono accent-text">None</code>, <code class="mono accent-text">prev</code> is the new head.</li>
        </ol>''',
    python_code='''from typing import Optional

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        prev = None
        curr = head

        while curr:
            next_node = curr.next
            curr.next = prev
            prev = curr
            curr = next_node

        return prev''',
    sidebar=LINKED_LIST_SIDEBAR,
    prev_next_html=prev_next(None, None, None, None),
    trace_js='''
    const VALS = [1, 2, 3, 4, 5];
    let steps = [], stepIndex = -1;

    function computeSteps() {
      // node i's "next" pointer target index, -1 means null. Starts as i+1 (forward list).
      steps = [];
      let nextPtr = VALS.map((_, i) => i + 1 < VALS.length ? i + 1 : -1);
      let prev = -1, curr = 0;
      steps.push({ prev, curr, nextPtr: [...nextPtr], action: 'start' });
      while (curr !== -1) {
        const nextNode = nextPtr[curr];
        nextPtr[curr] = prev;
        prev = curr;
        curr = nextNode;
        steps.push({ prev, curr, nextPtr: [...nextPtr], action: 'flip' });
      }
    }

    function buildTrace() {
      computeSteps(); stepIndex = -1;
      renderListStructure(steps[0].nextPtr, -1, 0);
      document.getElementById('trace-caption').textContent = 'Click "Next" to begin.';
      updateStepControls();
    }

    function renderListStructure(nextPtr, prevIdx, currIdx) {
      const track = document.getElementById('array-track');
      // order nodes left-to-right by original index for stable visual layout
      let html = '';
      VALS.forEach((v, i) => {
        const isCur = i === currIdx, isPrev = i === prevIdx;
        html += `<div class="ll-node">
          <div class="ll-box ${isCur ? 'cur' : ''} ${isPrev ? 'prev' : ''}">${v}
            ${isCur ? '<span class="ll-label" style="color:var(--trace-scan)">curr</span>' : ''}
            ${isPrev ? '<span class="ll-label" style="color:var(--trace-hit)">prev</span>' : ''}
          </div>
          <span class="ll-arrow">${nextPtr[i] === -1 ? '→ ∅' : (nextPtr[i] > i ? '→' : '←')}</span>
        </div>`;
      });
      track.innerHTML = html;
    }

    function renderStep() {
      const caption = document.getElementById('trace-caption');
      if (stepIndex < 0) {
        renderListStructure(steps[0].nextPtr, -1, 0);
        caption.textContent = 'Click "Next" to begin.'; updateStepControls(); return;
      }
      const s = steps[stepIndex];
      renderListStructure(s.nextPtr, s.prev, s.curr);
      if (s.action === 'start') {
        caption.textContent = `prev=None, curr=head (node ${VALS[s.curr]})`;
      } else if (s.curr === -1) {
        caption.textContent = `curr is None → reversal complete. New head is node ${VALS[s.prev]}.`;
      } else {
        caption.textContent = `Flipped node ${VALS[s.prev]}'s pointer backward. Now prev=${VALS[s.prev]}, curr=${VALS[s.curr]}.`;
      }
      updateStepControls();
    }

    function updateStepControls() {
      document.getElementById('step-counter').textContent = `Step ${stepIndex + 1} / ${steps.length}`;
      document.getElementById('btn-prev').disabled = stepIndex < 0;
      document.getElementById('btn-next').disabled = stepIndex >= steps.length - 1;
    }
'''
))

# ---------- 10. search-in-rotated-sorted-array ----------
problems.append(dict(
    slug='search-in-rotated-sorted-array', title='Search in Rotated Sorted Array', category='Array',
    difficulty='Medium', tags=['Binary Search', 'Array'],
    leetcode_url='https://leetcode.com/problems/search-in-rotated-sorted-array/',
    statement_html='''<p class="leading-relaxed mb-4">You are given an integer array <code class="mono px-1.5 py-0.5 rounded" style="background:var(--rail)">nums</code>, sorted in ascending order and rotated at an unknown pivot, and an integer <code class="mono px-1.5 py-0.5 rounded" style="background:var(--rail)">target</code>. Return the index of <code class="mono px-1.5 py-0.5 rounded" style="background:var(--rail)">target</code>, or <code class="mono px-1.5 py-0.5 rounded" style="background:var(--rail)">-1</code> if it isn\'t present.</p>
        <p class="text-soft text-sm mb-5">All values are unique. You must solve it in <span class="mono accent-text">O(log n)</span> time.</p>''',
    example_html='<p class="mb-1"><span class="text-soft">Input:</span> nums = [4,5,6,7,0,1,2], target = 0</p><p><span class="text-soft">Output:</span> 4</p>',
    trace_html='<div id="array-track" class="flex gap-3 pb-7 pt-7"></div>',
    quiz_time_opts=['O(1)', 'O(log n)', 'O(n)', 'O(n log n)'], quiz_space_opts=['O(1)', 'O(n)', 'O(log n)'],
    time_big='O(log n)', time_explain='The search window halves every iteration, even with the rotation.',
    space_big='O(1)', space_explain='Only three index pointers are tracked.',
    tricks=GENERIC_TRICKS + ['<strong class="accent-text">One half is always fully sorted.</strong> Even in a rotated array, comparing nums[low] to nums[mid] tells you instantly which half is normally ordered — then a simple range check tells you if the target could be there.'],
    approach_html='''<p class="mb-3">A rotated sorted array still has one useful property: <strong>at least one half of any window is always fully sorted.</strong> Standard binary search, but at each step you first figure out which half is sorted, then decide whether the target could live there.</p>
        <ol class="list-decimal list-inside space-y-2 text-soft">
          <li>Compute <code class="mono accent-text">mid</code>. If <code class="mono accent-text">nums[mid] === target</code>, return <code class="mono accent-text">mid</code>.</li>
          <li>If <code class="mono accent-text">nums[low] &lt;= nums[mid]</code>, the left half is sorted.</li>
          <li>Check whether <code class="mono accent-text">target</code> falls inside that sorted half\'s range — if so, search there; otherwise search the other half.</li>
          <li>Repeat until the window closes or the target is found.</li>
        </ol>''',
    python_code='''from typing import List

class Solution:
    def search(self, nums: List[int], target: int) -> int:
        left, right = 0, len(nums) - 1

        while left <= right:
            mid = (left + right) // 2

            if nums[mid] == target:
                return mid

            if nums[left] <= nums[mid]:
                if nums[left] <= target < nums[mid]:
                    right = mid - 1
                else:
                    left = mid + 1
            else:
                if nums[mid] < target <= nums[right]:
                    left = mid + 1
                else:
                    right = mid - 1

        return -1''',
    sidebar=ARRAY_SIDEBAR,
    prev_next_html=prev_next('container-with-most-water', 'Container With Most Water', 'longest-consecutive-sequence', 'Longest Consecutive Sequence'),
    trace_js='''
    const NUMS = [4, 5, 6, 7, 0, 1, 2];
    const TARGET = 0;
    let steps = [], stepIndex = -1;

    function computeSteps() {
      steps = [];
      let low = 0, high = NUMS.length - 1;
      while (low <= high) {
        const mid = Math.floor((low + high) / 2);
        if (NUMS[mid] === TARGET) { steps.push({ low, mid, high, found: true }); break; }
        const leftSorted = NUMS[low] <= NUMS[mid];
        let goRight;
        if (leftSorted) goRight = !(TARGET >= NUMS[low] && TARGET < NUMS[mid]);
        else goRight = (TARGET > NUMS[mid] && TARGET <= NUMS[high]);
        steps.push({ low, mid, high, leftSorted, goRight, found: false });
        if (goRight) low = mid + 1; else high = mid - 1;
      }
    }

    function buildTrace() {
      computeSteps(); stepIndex = -1;
      const track = document.getElementById('array-track');
      track.innerHTML = NUMS.map((n, i) => `<div class="cell" id="cell-${i}">${n}<span class="idx">i=${i}</span><span class="ptr" id="ptr-${i}"></span></div>`).join('');
      document.getElementById('trace-caption').textContent = 'Click "Next" to begin.';
      updateStepControls();
    }

    function setPointers(low, mid, high) {
      NUMS.forEach((_, i) => {
        const p = document.getElementById(`ptr-${i}`);
        let labels = [];
        if (i === low) labels.push('low');
        if (i === mid) labels.push('mid');
        if (i === high) labels.push('high');
        p.textContent = labels.join('/');
        p.style.opacity = labels.length ? 1 : 0;
      });
    }

    function renderStep() {
      const caption = document.getElementById('trace-caption');
      if (stepIndex < 0) {
        NUMS.forEach((_, i) => { document.getElementById(`cell-${i}`).classList.remove('discarded', 'scan', 'hit'); document.getElementById(`ptr-${i}`).style.opacity = 0; });
        caption.textContent = 'Click "Next" to begin.'; updateStepControls(); return;
      }
      const s = steps[stepIndex];
      NUMS.forEach((_, i) => {
        document.getElementById(`cell-${i}`).classList.toggle('discarded', i < s.low || i > s.high);
        document.getElementById(`cell-${i}`).classList.remove('scan', 'hit');
      });
      setPointers(s.low, s.mid, s.high);
      if (s.found) {
        document.getElementById(`cell-${s.mid}`).classList.add('hit');
        caption.textContent = `nums[${s.mid}] === target → return ${s.mid}`;
      } else {
        document.getElementById(`cell-${s.mid}`).classList.add('scan');
        caption.textContent = `mid=${s.mid} → ${s.leftSorted ? 'left half sorted' : 'right half sorted'} → search ${s.goRight ? 'right' : 'left'} half`;
      }
      updateStepControls();
    }

    function updateStepControls() {
      document.getElementById('step-counter').textContent = `Step ${stepIndex + 1} / ${steps.length}`;
      document.getElementById('btn-prev').disabled = stepIndex < 0;
      document.getElementById('btn-next').disabled = stepIndex >= steps.length - 1;
    }
'''
))

os.makedirs(OUT_DIR, exist_ok=True)
for p in problems:
    out = render(p)
    path = os.path.join(OUT_DIR, p['slug'] + '.html')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(out)
    print('wrote', path, len(out), 'bytes')
