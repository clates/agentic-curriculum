"""
Body Explorer — the interactive companion to the Body Team Week packet.

``build_html()`` returns one self-contained HTML file (inline SVG + JS, no network, no
dependencies). A simplified front-view body the student can pan and zoom, with one scene per
day of the week — lungs, heart, digestion, liver and kidneys, brain — plus a Whole Team view.

Circulation model: every trip is heart → lungs → heart → one body part (head, an arm or a leg)
→ U-turn in the capillaries → heart. Cells turn bright red only at the lungs and dark red only
at the U-turn, and the drawn vessels are generated from the same routes the cells ride, so the
picture and the motion can't disagree. Bright cells carry a white oxygen "backpack" they drop at
the U-turn; dark cells carry a gray carbon-dioxide "trash" bubble they drop at the lungs.

Open ``body_explorer.html#tue`` (mon/tue/wed/thu/fri/team) to start on a given day.
Emitted by ``generate_body_week_series.py``; not meant to be run on its own.
"""

EXPLORER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rudy's Rounds — Body Explorer</title>
<style>
  :root { --accent: #b91c1c; }
  * { box-sizing: border-box; }
  html, body { margin: 0; height: 100%; font-family: 'Trebuchet MS', Arial, sans-serif; color: #0f172a; }
  .app { display: flex; height: 100vh; }
  .stage-wrap { position: relative; flex: 1; min-width: 0; overflow: hidden;
    background: radial-gradient(circle at 50% 40%, #1e3a5f, #0b1220); }
  .stage-wrap.light { background: radial-gradient(circle at 50% 40%, #ffffff, #dbeafe); }
  svg#stage { width: 100%; height: 100%; display: block; touch-action: none; cursor: grab; user-select: none; }
  svg#stage.dragging { cursor: grabbing; }
  button { font: inherit; font-weight: bold; border: none; border-radius: 10px; padding: 9px 13px;
    cursor: pointer; background: #fff; color: #0f172a; box-shadow: 0 2px 6px rgba(0,0,0,.35); font-size: 16px; }
  button:focus-visible { outline: 3px solid #fde047; outline-offset: 2px; }
  .days { position: absolute; top: 10px; left: 10px; right: 10px; display: flex; flex-wrap: wrap; gap: 6px; }
  .days button { color: #fff; }
  .days button[aria-pressed="true"] { outline: 3px solid #fde047; outline-offset: 1px; transform: translateY(1px); }
  .zoom { position: absolute; right: 10px; bottom: 10px; display: flex; flex-direction: column; gap: 6px; }
  .zoom button { width: 48px; height: 48px; font-size: 22px; padding: 0; }
  .toggles { position: absolute; left: 10px; bottom: 56px; right: 70px; display: flex; flex-wrap: wrap; gap: 6px; }
  .toggles button.on { background: #fde047; }
  .readout { position: absolute; left: 10px; bottom: 10px; background: rgba(255,255,255,.94);
    border-radius: 10px; padding: 7px 12px; font-size: 16px; font-weight: bold; }
  .toast { position: absolute; top: 66px; left: 50%; transform: translateX(-50%); background: #fde047;
    padding: 9px 18px; border-radius: 999px; font-weight: bold; font-size: 17px; opacity: 0; transition: opacity .35s;
    pointer-events: none; white-space: nowrap; box-shadow: 0 2px 8px rgba(0,0,0,.4); }
  .toast.show { opacity: 1; }
  .panel { width: 400px; background: #fff; overflow-y: auto; padding: 18px 20px 26px;
    border-left: 8px solid var(--accent); font-size: 18px; }
  .panel h1 { font-size: 14px; margin: 0 0 4px; color: #64748b; text-transform: uppercase; letter-spacing: .08em; }
  .panel h2 { font-size: 28px; margin: 0 0 6px; color: var(--accent); }
  .panel h3 { font-size: 15px; text-transform: uppercase; letter-spacing: .06em; color: #334155; margin: 18px 0 6px; }
  .rudy-says { display: flex; gap: 12px; align-items: flex-start; margin: 12px 0; }
  .rudy-says svg { flex: 0 0 60px; }
  .bubble { background: #fee2e2; border-radius: 14px; padding: 10px 14px; font-size: 22px; line-height: 1.35; }
  .panel ul { padding-left: 22px; margin: 0; line-height: 1.45; }
  .panel li { margin-bottom: 6px; }
  .card { border: 2px solid #e2e8f0; border-radius: 12px; padding: 12px 14px; line-height: 1.45; }
  .card b { color: var(--accent); font-size: 21px; }
  .card .crew { display: inline-block; font-size: 13px; font-weight: bold; color: #fff; background: var(--accent);
    border-radius: 999px; padding: 2px 9px; margin-left: 8px; vertical-align: 3px; }
  .key { margin-top: 12px; line-height: 1.5; }
  .key div { display: flex; gap: 10px; align-items: center; margin-bottom: 6px; }
  .key svg { flex: 0 0 34px; }
  .extra { margin-top: 14px; }
  .meter { height: 18px; border-radius: 9px; background: #e2e8f0; overflow: hidden; margin: 6px 0; }
  .meter > div { height: 100%; background: #38bdf8; transition: width .3s; }
  .game { border: 2px dashed #94a3b8; border-radius: 12px; padding: 10px; text-align: center; }
  .ruler-box { position: relative; height: 330px; width: 140px; margin: 6px auto; overflow: hidden; }
  .ruler { position: absolute; left: 50px; top: 0; width: 38px; height: 180px; border: 2px solid #92400e;
    border-radius: 3px; background: repeating-linear-gradient(to top, #fde68a 0 5px, #b45309 5px 6px); }
  .ruler span { position: absolute; left: 3px; font-size: 12px; font-weight: bold; color: #451a03;
    background: #fde68a; padding: 0 2px; transform: translateY(50%); }
  .hand { position: absolute; left: 44px; top: 162px; font-size: 42px; line-height: 1; pointer-events: none; }
  #gameMsg { min-height: 48px; margin: 6px 0; }
  #tries { text-align: left; }
  details.teacher { margin-top: 22px; border-top: 2px solid #e2e8f0; padding-top: 10px; font-size: 15px; color: #334155; }
  details.teacher summary { cursor: pointer; font-weight: bold; font-size: 16px; }
  details.teacher p { margin: 8px 0; line-height: 1.5; }
  .organ { transition: opacity .5s; }
  .organ.dim { opacity: .14; }
  .organ.hidden { display: none; }
  .lbl { transition: opacity .4s; pointer-events: none; }
  .lbl text { font-size: 18px; font-weight: bold; fill: #fff; paint-order: stroke; stroke: #0f172a; stroke-width: 4px; stroke-linejoin: round; }
  .lbl line { stroke: #e2e8f0; stroke-width: 1.6; }
  .lbl circle { fill: #e2e8f0; stroke: #0f172a; stroke-width: 1; }
  .light .lbl text { fill: #0f172a; stroke: #fff; }
  .light .lbl line { stroke: #334155; }
  .light .lbl circle { fill: #334155; stroke: #fff; }
  .worldtext { font-size: 26px; font-weight: bold; fill: #fde047; paint-order: stroke; stroke: #0f172a;
    stroke-width: 5px; pointer-events: none; }
  @media (max-width: 820px) {
    .app { flex-direction: column; height: auto; }
    .stage-wrap { height: 64vh; flex: none; }
    .panel { width: auto; border-left: none; border-top: 8px solid var(--accent); }
    button { font-size: 13px; padding: 6px 9px; border-radius: 8px; }
    .zoom button { width: 38px; height: 38px; font-size: 18px; }
    .toggles { right: 58px; bottom: 46px; }
    .readout { font-size: 12px; padding: 5px 8px; }
    .bubble { font-size: 19px; }
  }
</style>
</head>
<body>
<div class="app">
<div class="stage-wrap" id="stageWrap">
<svg id="stage" viewBox="-160 0 920 1000" preserveAspectRatio="xMidYMid meet" role="img"
     aria-label="A simplified human body. Drag to look around, scroll or pinch to zoom, tap an organ to learn its job.">
  <defs>
    <filter id="glow" x="-1" y="-1" width="3" height="3">
      <feGaussianBlur stdDeviation="2.5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="rudyGlow" x="-1" y="-1" width="3" height="3">
      <feGaussianBlur stdDeviation="5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <clipPath id="bladderClip"><ellipse cx="300" cy="708" rx="26" ry="18"/></clipPath>
  </defs>
  <g id="world">
    <!-- Body silhouette -->
    <g id="body">
      <g stroke="#c08a68" stroke-linecap="round" fill="none">
        <line x1="195" y1="275" x2="130" y2="610" stroke-width="58"/>
        <line x1="405" y1="275" x2="470" y2="610" stroke-width="58"/>
        <line x1="262" y1="700" x2="250" y2="975" stroke-width="80"/>
        <line x1="338" y1="700" x2="350" y2="975" stroke-width="80"/>
      </g>
      <g stroke="#f6d7bf" stroke-linecap="round" fill="none">
        <line x1="195" y1="275" x2="130" y2="610" stroke-width="52"/>
        <line x1="405" y1="275" x2="470" y2="610" stroke-width="52"/>
        <line x1="262" y1="700" x2="250" y2="975" stroke-width="74"/>
        <line x1="338" y1="700" x2="350" y2="975" stroke-width="74"/>
      </g>
      <path d="M 245 230 L 355 230 Q 415 236 420 285 L 412 560 Q 408 690 370 735 L 230 735 Q 192 690 188 560 L 180 285 Q 185 236 245 230 Z"
            fill="#f6d7bf" stroke="#c08a68" stroke-width="3"/>
      <rect x="272" y="180" width="56" height="64" rx="12" fill="#f6d7bf"/>
      <ellipse cx="300" cy="112" rx="72" ry="86" fill="#f6d7bf" stroke="#c08a68" stroke-width="3"/>
    </g>

    <!-- Vessels drawn under the organs (generated from the routes in the script) -->
    <g class="organ" data-organ="vessels" id="vesselsBody" fill="none" stroke-linecap="round" stroke-linejoin="round">
      <path d="M 314 560 L 258 576 M 314 560 L 343 576" stroke="#ef4444" stroke-width="3"/>
    </g>

    <!-- Kidneys sit in the back, behind the gut: dashed outline -->
    <g class="organ" data-organ="kidneys">
      <path d="M 245 545 C 230 545 222 560 222 578 C 222 598 232 610 247 610 C 258 610 262 600 256 590 C 252 582 252 572 256 565 C 262 555 258 545 245 545 Z"
            fill="#be123c" stroke="#881337" stroke-width="3" stroke-dasharray="6 3"/>
      <path d="M 355 545 C 370 545 378 560 378 578 C 378 598 368 610 353 610 C 342 610 338 600 344 590 C 348 582 348 572 344 565 C 338 555 342 545 355 545 Z"
            fill="#be123c" stroke="#881337" stroke-width="3" stroke-dasharray="6 3"/>
      <path id="ureterL" d="M 254 598 C 262 640 280 680 292 700" fill="none" stroke="#eab308" stroke-width="4"/>
      <path id="ureterR" d="M 346 598 C 338 640 320 680 308 700" fill="none" stroke="#eab308" stroke-width="4"/>
      <path id="renalL" d="M 314 560 L 258 576" fill="none" stroke="none"/>
      <path id="renalR" d="M 314 560 L 343 576" fill="none" stroke="none"/>
    </g>

    <!-- Liver (body's right = viewer's left) with the gallbladder -->
    <g class="organ" data-organ="liver">
      <path d="M 196 492 C 230 478 300 478 330 492 C 335 505 322 520 300 528 C 270 545 230 560 210 552 C 196 540 192 510 196 492 Z"
            fill="#9a3412" stroke="#7c2d12" stroke-width="3"/>
      <ellipse cx="268" cy="538" rx="10" ry="7" fill="#65a30d" stroke="#3f6212" stroke-width="2"/>
      <path id="portalPath" d="M 300 612 C 296 582 285 552 268 528" fill="none" stroke="none"/>
    </g>

    <!-- Stomach (viewer's right) -->
    <g class="organ" data-organ="stomach">
      <g id="stomachInner">
        <path d="M 345 510 C 365 495 400 500 402 530 C 405 565 385 590 355 592 C 335 593 318 585 310 575 C 322 572 340 568 352 558 C 366 545 360 525 345 510 Z"
              fill="#fbcfe8" stroke="#db2777" stroke-width="3"/>
      </g>
    </g>

    <!-- Large intestine frames the small intestine -->
    <g class="organ" data-organ="largeInt">
      <path d="M 250 690 C 236 690 232 670 232 650 L 232 615 C 232 602 240 597 255 597 L 345 597 C 360 597 368 602 368 615 L 368 655 C 368 680 350 690 330 690 C 318 690 312 700 310 712"
            fill="none" stroke="#b45309" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/>
      <path id="largePath" d="M 250 690 C 236 690 232 670 232 650 L 232 615 C 232 602 240 597 255 597 L 345 597 C 360 597 368 602 368 615 L 368 655 C 368 680 350 690 330 690 C 318 690 312 700 310 712"
            fill="none" stroke="#f59e0b" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>
    </g>

    <!-- Small intestine: the long coiled tube -->
    <g class="organ" data-organ="smallInt">
      <path d="M 310 578 C 290 590 262 605 262 615 C 262 628 338 622 338 636 C 338 650 262 644 262 658 C 262 672 338 666 338 680 C 338 690 300 690 280 688 C 268 687 258 690 250 690"
            fill="none" stroke="#be185d" stroke-width="13" stroke-linecap="round"/>
      <path id="smallPath" d="M 310 578 C 290 590 262 605 262 615 C 262 628 338 622 338 636 C 338 650 262 644 262 658 C 262 672 338 666 338 680 C 338 690 300 690 280 688 C 268 687 258 690 250 690"
            fill="none" stroke="#f9a8d4" stroke-width="8" stroke-linecap="round"/>
    </g>

    <!-- Bladder: pink, with a yellow urine level clipped to its shape -->
    <g class="organ" data-organ="bladder">
      <ellipse cx="300" cy="708" rx="26" ry="18" fill="#fdf2f8"/>
      <rect id="bladderFill" x="270" y="726" width="60" height="0" fill="#fde047" clip-path="url(#bladderClip)"/>
      <ellipse cx="300" cy="708" rx="26" ry="18" fill="none" stroke="#db2777" stroke-width="3"/>
    </g>

    <!-- Windpipe: grayish-white with rings (blue is avoided on purpose) -->
    <g class="organ" data-organ="windpipe">
      <path d="M 294 184 L 294 300" stroke="#9ca3af" stroke-width="15" stroke-linecap="round"/>
      <path d="M 294 184 L 294 300" stroke="#f1f5f9" stroke-width="11" stroke-linecap="round"/>
      <g stroke="#9ca3af" stroke-width="2">
        <line x1="288" y1="205" x2="300" y2="205"/><line x1="288" y1="225" x2="300" y2="225"/>
        <line x1="288" y1="245" x2="300" y2="245"/><line x1="288" y1="265" x2="300" y2="265"/>
        <line x1="288" y1="285" x2="300" y2="285"/>
      </g>
      <path d="M 294 300 Q 276 310 260 332 M 294 300 Q 314 310 336 332" fill="none" stroke="#9ca3af" stroke-width="11" stroke-linecap="round"/>
      <path d="M 294 300 Q 276 310 260 332 M 294 300 Q 314 310 336 332" fill="none" stroke="#f1f5f9" stroke-width="7" stroke-linecap="round"/>
    </g>

    <!-- Lungs: the body's right lung (viewer's left) is bigger with three lobes;
         the left lung is smaller with a notch where the heart fits -->
    <g class="organ" data-organ="lungs">
      <g id="lungsInner">
        <path d="M 286 300 C 258 282 210 296 200 350 C 190 402 194 452 202 472 C 234 482 270 477 290 466 C 292 420 292 360 286 300 Z"
              fill="#fda4af" stroke="#e11d48" stroke-width="3"/>
        <path d="M 310 300 C 338 286 378 300 388 350 C 396 398 396 446 390 466 C 374 472 362 472 354 468 C 352 448 340 432 326 424 C 314 405 312 360 310 300 Z"
              fill="#fda4af" stroke="#e11d48" stroke-width="3"/>
        <g fill="none" stroke="#e11d48" stroke-width="1.8" opacity=".7">
          <path d="M 206 382 L 284 360"/><path d="M 204 430 L 288 420"/><path d="M 386 372 L 318 396"/>
        </g>
        <g fill="#fecdd3" stroke="#e11d48" stroke-width="1">
          <circle cx="236" cy="372" r="5"/><circle cx="244" cy="376" r="5"/><circle cx="238" cy="381" r="5"/>
          <circle cx="368" cy="374" r="5"/><circle cx="376" cy="378" r="5"/><circle cx="370" cy="383" r="5"/>
        </g>
      </g>
    </g>
    <!-- Lung vessels drawn on top of the lungs: dark blood in, bright blood out -->
    <g class="organ" data-organ="vessels" id="vesselsLung" fill="none" stroke-linecap="round" stroke-linejoin="round"></g>

    <!-- Esophagus: its own tube from the mouth to the stomach, beside the windpipe -->
    <g class="organ" data-organ="esophagus">
      <path d="M 304 176 C 312 184 314 196 314 210 L 314 300 C 315 360 316 420 320 462 C 324 490 335 505 345 515"
            fill="none" stroke="#a16207" stroke-width="13" stroke-linecap="round"/>
      <path id="esoPath" d="M 304 176 C 312 184 314 196 314 210 L 314 300 C 315 360 316 420 320 462 C 324 490 335 505 345 515"
            fill="none" stroke="#e7b98f" stroke-width="9" stroke-linecap="round"/>
    </g>

    <!-- Heart: middle of the chest, tipped toward the body's left (viewer's right) -->
    <g class="organ" data-organ="heart">
      <g id="heartInner" transform="translate(322 415) rotate(-35) scale(1.45)">
        <path d="M 0 22 C -30 0 -38 -22 -22 -34 C -10 -42 0 -34 0 -24 C 0 -34 10 -42 22 -34 C 38 -22 30 0 0 22 Z"
              fill="#dc2626" stroke="#7f1d1d" stroke-width="2.4"/>
        <path d="M -2 -20 C 2 -8 -2 4 2 14" fill="none" stroke="#7f1d1d" stroke-width="1.6" opacity=".7"/>
      </g>
    </g>

    <!-- Diaphragm: the dome-shaped muscle under the lungs -->
    <g class="organ" data-organ="diaphragm">
      <path id="diaphragmPath" d="M 195 482 Q 300 430 405 482" fill="none" stroke="#ea580c" stroke-width="8" stroke-linecap="round"/>
    </g>

    <!-- Nose and mouth: where air and food come in. Thin dashed passages lead to the throat. -->
    <g class="organ" data-organ="mouth">
      <path d="M 300 116 L 291 146 Q 300 154 309 146 Z" fill="#efc4a4" stroke="#c08a68" stroke-width="2"/>
      <ellipse cx="295" cy="148" rx="3.2" ry="2.2" fill="#5b3a29"/><ellipse cx="305" cy="148" rx="3.2" ry="2.2" fill="#5b3a29"/>
      <ellipse cx="300" cy="170" rx="15" ry="7" fill="#7f1d1d" stroke="#9f1239" stroke-width="2"/>
      <ellipse cx="300" cy="173" rx="8" ry="3" fill="#f472b6"/>
      <g fill="none" stroke="#64748b" stroke-width="2" stroke-dasharray="3 3">
        <path d="M 300 150 C 300 160 296 172 294 184"/>
      </g>
    </g>

    <!-- Brain and brain stem (the stem sits behind the face: faint, dashed) -->
    <g class="organ" data-organ="brain">
      <rect x="294" y="126" width="12" height="54" rx="6" fill="#f9a8d4" fill-opacity=".3" stroke="#be185d"
            stroke-width="1.5" stroke-dasharray="4 3" stroke-opacity=".55"/>
      <ellipse id="brainShape" cx="300" cy="88" rx="58" ry="46" fill="#f9a8d4" stroke="#be185d" stroke-width="3"/>
      <g fill="none" stroke="#be185d" stroke-width="2" stroke-linecap="round" opacity=".75">
        <path d="M 300 44 L 300 132"/>
        <path d="M 252 78 C 262 66 272 86 282 72"/><path d="M 256 104 C 266 92 276 112 286 98"/>
        <path d="M 318 72 C 328 86 338 66 348 78"/><path d="M 314 98 C 324 112 334 92 344 104"/>
        <path d="M 266 56 C 274 50 280 60 288 54"/><path d="M 312 54 C 320 60 326 50 334 56"/>
      </g>
    </g>

    <!-- Senses: eyes and ears send messages IN -->
    <g class="organ" data-organ="senses">
      <ellipse cx="276" cy="126" rx="10" ry="7" fill="#fff" stroke="#334155" stroke-width="2"/>
      <ellipse cx="324" cy="126" rx="10" ry="7" fill="#fff" stroke="#334155" stroke-width="2"/>
      <circle cx="276" cy="126" r="4" fill="#1e3a8a"/><circle cx="324" cy="126" r="4" fill="#1e3a8a"/>
      <ellipse cx="229" cy="118" rx="10" ry="18" fill="#f2c4a6" stroke="#c08a68" stroke-width="2.5"/>
      <ellipse cx="371" cy="118" rx="10" ry="18" fill="#f2c4a6" stroke="#c08a68" stroke-width="2.5"/>
    </g>

    <!-- Nerves: only shown on Brain day, so yellow never reads as a third kind of blood -->
    <g class="organ hidden" data-organ="nerves">
      <path d="M 300 132 L 300 690" stroke="#facc15" stroke-width="7" stroke-linecap="round"/>
      <g stroke="#facc15" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path d="M 300 280 L 205 300 L 140 600"/>
        <path d="M 300 280 L 395 300 L 460 600"/>
        <path d="M 300 690 L 262 720 L 252 960"/>
        <path d="M 300 690 L 338 720 L 348 960"/>
        <path d="M 300 420 L 230 450"/><path d="M 300 420 L 370 450"/>
        <path d="M 300 560 L 240 590"/><path d="M 300 560 L 360 590"/>
      </g>
    </g>

    <!-- Invisible guide paths for animations -->
    <g id="guides" fill="none" stroke="none" style="pointer-events:none">
      <path id="airL" d="M 300 150 C 300 160 296 172 294 184 L 294 300 L 260 332 L 240 376"/>
      <path id="airR" d="M 300 150 C 300 160 296 172 294 184 L 294 300 L 336 332 L 372 378"/>
      <path id="eyePath" d="M 276 126 C 283 112 292 100 300 92"/>
      <path id="earPath" d="M 371 118 C 355 108 335 100 305 92"/>
      <path id="handPath" d="M 300 100 L 300 280 L 205 300 L 140 600"/>
      <path id="legPath" d="M 300 100 L 300 690 L 262 720 L 252 960"/>
    </g>
    <g id="routes" fill="none" stroke="none" style="pointer-events:none"></g>
    <g id="cells" style="pointer-events:none"></g>
    <g id="fx" style="pointer-events:none"></g>
    <g id="rudyLayer"></g>
    <g id="labels"></g>
    <text id="breathText" class="worldtext" x="232" y="290" text-anchor="middle" opacity="0"></text>
  </g>
</svg>
<div class="days" id="days" role="toolbar" aria-label="Choose a day"></div>
<div class="toggles">
  <button id="sprintBtn" aria-pressed="false">🏃 Sprint!</button>
  <button id="followBtn" aria-pressed="false">🔴 Follow Rudy</button>
  <button id="labelsBtn" aria-pressed="true" class="on">🏷️ Labels</button>
</div>
<div class="readout" id="readout"></div>
<div class="zoom">
  <button id="zoomIn" aria-label="Zoom in">+</button>
  <button id="zoomOut" aria-label="Zoom out">−</button>
  <button id="zoomReset" aria-label="Show the whole body">⤢</button>
</div>
<div class="toast" id="toast" role="status"></div>
</div>

<aside class="panel">
  <h1>Rudy's Rounds · Body Explorer</h1>
  <h2 id="dayTitle"></h2>
  <div class="rudy-says">
    <svg viewBox="-13 -13 26 26" width="60" height="60" aria-hidden="true">
      <circle r="12" fill="#dc2626" stroke="#7f1d1d" stroke-width="1.5"/>
      <circle r="6" fill="#b91c1c"/>
      <circle cx="-4" cy="-3" r="2.2" fill="#fff"/><circle cx="4" cy="-3" r="2.2" fill="#fff"/>
      <circle cx="-4" cy="-3" r="1" fill="#111"/><circle cx="4" cy="-3" r="1" fill="#111"/>
      <path d="M -4 4 Q 0 7 4 4" fill="none" stroke="#fff" stroke-width="1.4" stroke-linecap="round"/>
    </svg>
    <div class="bubble" id="rudySays"></div>
  </div>
  <h3>Watch it work</h3>
  <ul id="watch"></ul>
  <div class="extra" id="extra"></div>
  <div class="key" id="key"></div>
  <h3>Tap an organ</h3>
  <div class="card" id="info">Tap any organ, or Rudy himself, to see its job.</div>
  <details class="teacher">
    <summary>Teacher</summary>
    <p><button id="lightBtn" aria-pressed="false">☀️ Light background</button></p>
    <p>Drag to look around. Scroll or pinch to zoom. Keys: 1–5 for Monday–Friday, 6 for the whole team,
      arrows to pan, + and − to zoom, space to catch in the Ruler Drop.</p>
    <p>Links that open on one day: add <code>#mon</code>, <code>#tue</code>, <code>#wed</code>, <code>#thu</code>,
      <code>#fri</code> or <code>#team</code> to the end of the file address.</p>
    <p>A simplified model: real organs overlap and sit at different depths. The kidneys (dashed) are in the back,
      and the esophagus really runs behind the windpipe and heart. Each trip in the model is heart → lungs →
      heart → one body part → heart. Real blood returning to the heart still carries most of its oxygen.</p>
  </details>
</aside>
</div>

<script>
"use strict";
const NS = "http://www.w3.org/2000/svg";
const $ = (id) => document.getElementById(id);
const svg = $("stage"), world = $("world"), fx = $("fx"), cellsLayer = $("cells");
const mk = (tag, attrs, parent) => {
  const el = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
  if (parent) parent.appendChild(el);
  return el;
};

const ORGANS = {
  mouth: { name: "Nose & mouth", crew: "Air & Fuel Crews",
    job: "Air comes in through your nose and mouth. Food comes in through your mouth, where teeth and saliva get to work.",
    fact: "Hairs and sticky mucus in your nose trap dust before it reaches your lungs." },
  lungs: { name: "Lungs", crew: "Air Crew", job: "Load oxygen into the blood and send carbon dioxide out.",
    fact: "Your left lung is smaller and has a notch, to leave room for your heart." },
  windpipe: { name: "Windpipe", crew: "Air Crew", job: "Carries AIR from your throat down to your lungs.",
    fact: "Stiff rings keep it open, and it splits into smaller tubes like an upside-down tree." },
  diaphragm: { name: "Diaphragm", crew: "Air Crew", job: "Pulls DOWN so air rushes into your lungs.",
    fact: "Hiccups happen when your diaphragm twitches!" },
  heart: { name: "Heart", crew: "Pump Crew", job: "Pumps blood all over your body.",
    fact: "It is about the size of your fist. Blood goes through it twice on every trip!" },
  vessels: { name: "Arteries & veins", crew: "Pump Crew",
    job: "Arteries carry blood AWAY from the heart. Veins bring it BACK. Tiny capillaries make the U-turn.",
    fact: "Blood is always red. Veins only look blue through your skin." },
  esophagus: { name: "Esophagus", crew: "Fuel Crew", job: "Squeezes FOOD down from your mouth to your stomach.",
    fact: "It is a different tube from the windpipe, and it works even upside down — astronauts swallow in space!" },
  stomach: { name: "Stomach", crew: "Fuel Crew", job: "Churns food with acid into a thick soup.",
    fact: "A slimy lining keeps the acid from hurting the stomach itself." },
  smallInt: { name: "Small intestine", crew: "Fuel Crew", job: "Soaks nutrients from food into the blood.",
    fact: "A grown-up's is about 20 feet long, all coiled up in the belly." },
  largeInt: { name: "Large intestine", crew: "Fuel Crew", job: "Soaks up leftover water. Waste leaves the body.",
    fact: "It is shorter than the small intestine, but wider." },
  liver: { name: "Liver & gallbladder", crew: "Clean-Up Crew",
    job: "The liver cleans harmful stuff out of the blood, stores fuel, and makes bile. The little green gallbladder holds the bile.",
    fact: "The liver is the biggest organ inside your body, and it can grow back!" },
  kidneys: { name: "Kidneys", crew: "Clean-Up Crew", job: "Filter waste and extra water out of the blood to make urine.",
    fact: "You have two. They sit in your back, one on each side of your spine." },
  bladder: { name: "Bladder", crew: "Clean-Up Crew", job: "Holds urine until you go to the bathroom.",
    fact: "It stretches like a balloon as it fills." },
  brain: { name: "Brain", crew: "Coaching Staff",
    job: "The Head Coach: gets messages from your senses and tells your body what to do.",
    fact: "It uses about one fifth of all the oxygen Rudy carries. The brain stem keeps you breathing, even asleep." },
  nerves: { name: "Spinal cord & nerves", crew: "Coaching Staff",
    job: "Carry messages between your brain and your body. The spinal cord runs down your back.",
    fact: "Messages zip along some nerves faster than a race car." },
  senses: { name: "Eyes & ears", crew: "Coaching Staff", job: "Send messages about the world IN to your brain.",
    fact: "Your eyes collect light, but it's your brain that figures out what you're seeing." },
  rudy: { name: "Rudy the Red Blood Cell", crew: "Delivery Truck",
    job: "Carries oxygen from the lungs to every part of your body.",
    fact: "Bright red with a white bubble: carrying oxygen. Dark red with a gray bubble: dropped off some oxygen and is bringing trash gas back to the lungs." },
};

// Labels live in two columns outside the body, each with a leader line to its organ.
const LABELS = [
  { for: "brain", text: "Brain", side: "L", y: 74, t: [262, 82] },
  { for: "senses", text: "Eye", side: "L", y: 126, t: [266, 126] },
  { for: "mouth", text: "Nose & mouth", side: "L", y: 168, t: [287, 166] },
  { for: "windpipe", text: "Windpipe", side: "L", y: 240, t: [288, 240] },
  { for: "lungs", text: "Lungs", side: "L", y: 392, t: [214, 394] },
  { for: "liver", text: "Liver", side: "L", y: 496, t: [220, 504] },
  { for: "liver", text: "Gallbladder", side: "L", y: 540, t: [259, 539] },
  { for: "kidneys", text: "Kidney", side: "L", y: 584, t: [236, 566] },
  { for: "largeInt", text: "Large intestine", side: "L", y: 636, t: [232, 636] },
  { for: "nerves", text: "Spinal cord", side: "L", y: 700, t: [300, 640] },
  { for: "senses", text: "Ear", side: "R", y: 112, t: [380, 116] },
  { for: "esophagus", text: "Esophagus", side: "R", y: 222, t: [319, 222] },
  { for: "vessels", text: "Arteries & veins", side: "R", y: 292, t: [400, 304] },
  { for: "heart", text: "Heart", side: "R", y: 418, t: [350, 416] },
  { for: "diaphragm", text: "Diaphragm", side: "R", y: 474, t: [398, 477] },
  { for: "stomach", text: "Stomach", side: "R", y: 534, t: [394, 536] },
  { for: "kidneys", text: "Kidney", side: "R", y: 584, t: [366, 566] },
  { for: "smallInt", text: "Small intestine", side: "R", y: 646, t: [337, 650] },
  { for: "bladder", text: "Bladder", side: "R", y: 712, t: [326, 708] },
];

const DAYS = {
  mon: { tab: "Mon · Lungs", color: "#1d4ed8", title: "Monday · Breathe In!",
    organs: ["mouth", "windpipe", "lungs", "diaphragm"],
    rudy: "This is where I load up! In the lungs I drop my trash gas and pick up fresh oxygen.",
    watch: ["Air comes in through the nose and mouth, then down the windpipe.",
      "The orange diaphragm pulls DOWN: air rushes IN.",
      "Dark cells drop a gray trash bubble and pick up a white oxygen bubble. They turn bright red!",
      "Tap Sprint and watch the breathing speed up."] },
  tue: { tab: "Tue · Heart", color: "#15803d", title: "Tuesday · The Pump", organs: ["heart", "vessels"],
    fit: ["heart", "lungs"],
    rudy: "I visit the heart TWICE every trip: once on the way to the lungs, and once on the way out to the body!",
    watch: ["Every squeeze is one heartbeat: lub-dub!",
      "Bright red blood goes OUT in the arteries. It makes a U-turn in tiny capillaries and comes BACK darker in the veins.",
      "Tap Sprint: the heart AND the lungs speed up together. Teamwork!"] },
  wed: { tab: "Wed · Digestion", color: "#7c3aed", title: "Wednesday · The Fuel Factory",
    organs: ["mouth", "esophagus", "stomach", "smallInt", "largeInt"],
    rudy: "Food fuel doesn't ride on me. It floats in the blood river all around me!",
    watch: ["Follow the brown food bite: mouth, then down the esophagus (NOT the windpipe!).",
      "The stomach churns it into a thick soup.",
      "Yellow nutrients soak into the blood in the small intestine.",
      "Blue water drops soak up in the large intestine. The rest is waste."] },
  thu: { tab: "Thu · Clean-Up", color: "#c2410c", title: "Thursday · The Clean-Up Crew", organs: ["liver", "kidneys", "bladder"],
    rudy: "Cells make trash. The liver and kidneys clean my river so it stays safe!",
    watch: ["Gray waste goes into the two kidneys and comes out as yellow urine.",
      "Watch the bladder fill up like a balloon.",
      "Green sparkles: the liver making harmful stuff safe.",
      "Tap Drink water: more water makes paler pee!"] },
  fri: { tab: "Fri · Brain", color: "#0f766e", title: "Friday · The Head Coach", organs: ["brain", "nerves", "senses"],
    rudy: "My favorite stop! The brain uses about a fifth of all the oxygen I carry.",
    watch: ["Yellow lines are NERVES. Yellow flashes are messages zipping along them.",
      "Messages come IN from your eyes and ears, and go OUT to your muscles.",
      "Play the Ruler Drop below: how fast is YOUR brain?"] },
  team: { tab: "Whole Team", color: "#b91c1c", title: "The Whole Body Team", organs: [],
    rudy: "My trip: heart, lungs, heart, out to the body, and back to the heart. I make it in less than a minute!",
    watch: ["Find Rudy: the big glowing cell with a face.", "Tap any organ to learn its job.",
      "Tap Follow Rudy and ride along!", "Tap Sprint to see the whole team speed up at once."] },
};
const DAY_KEYS = ["mon", "tue", "wed", "thu", "fri", "team"];

const state = { day: "team", sprint: false, follow: false, labels: false, bpm: 90, brpm: 20,
  beat: 0, breath: 0, hydration: 0.35, bladder: 0.25, sceneT: 0, acc: {} };

// ---------- Camera: pan / zoom / fly ----------
const VB = { x: -160, w: 920, h: 1000 }, CX = VB.x + VB.w / 2, CY = 500;
const cam = { x: 0, y: 0, s: 1 };
let camAnim = null;
function applyCam() {
  world.setAttribute("transform", `translate(${cam.x.toFixed(2)} ${cam.y.toFixed(2)}) scale(${cam.s.toFixed(4)})`);
}
const clampS = (s) => Math.max(0.6, Math.min(7, s));
function toSvg(clientX, clientY) {
  const p = svg.createSVGPoint(); p.x = clientX; p.y = clientY;
  return p.matrixTransform(svg.getScreenCTM().inverse());
}
function zoomAt(px, py, f) {
  const ns = clampS(cam.s * f);
  cam.x = px - (px - cam.x) * (ns / cam.s);
  cam.y = py - (py - cam.y) * (ns / cam.s);
  cam.s = ns; applyCam();
}
function flyTo(target, ms = 900) { camAnim = { from: { ...cam }, to: target, t0: performance.now(), ms }; }
function fitBox(b) {
  const pad = 24, top = 70;  // leave room for the day buttons
  const s = clampS(Math.min(VB.w / (b.width + 2 * pad), (VB.h - top) / (b.height + 2 * pad)));
  return { s, x: CX - s * (b.x + b.width / 2), y: (VB.h + top) / 2 - s * (b.y + b.height / 2) };
}
function unionBox(els) {
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  els.forEach((el) => {
    const b = el.getBBox(); if (!b.width && !b.height) return;
    x0 = Math.min(x0, b.x); y0 = Math.min(y0, b.y); x1 = Math.max(x1, b.x + b.width); y1 = Math.max(y1, b.y + b.height);
  });
  return { x: x0, y: y0, width: x1 - x0, height: y1 - y0 };
}
function viewFor(names, withLabels) {
  const els = [];
  names.forEach((n) => document.querySelectorAll(`.organ[data-organ="${n}"]`).forEach((e) => els.push(e)));
  if (withLabels) names.forEach((n) => document.querySelectorAll(`.lbl[data-for="${n}"]`).forEach((e) => els.push(e)));
  return fitBox(unionBox(els));
}
let WHOLE = null;

const ptrs = new Map();
let pinchDist = null, downAt = null, moved = 0;
svg.addEventListener("pointerdown", (e) => {
  svg.setPointerCapture(e.pointerId);
  ptrs.set(e.pointerId, { p: toSvg(e.clientX, e.clientY), cx: e.clientX, cy: e.clientY });
  if (ptrs.size === 1) { downAt = [e.clientX, e.clientY]; moved = 0; }
  camAnim = null; svg.classList.add("dragging");
});
svg.addEventListener("pointermove", (e) => {
  const rec = ptrs.get(e.pointerId); if (!rec) return;
  const p = toSvg(e.clientX, e.clientY);
  if (ptrs.size === 1) {
    cam.x += p.x - rec.p.x; cam.y += p.y - rec.p.y; applyCam();
    moved = Math.max(moved, Math.hypot(e.clientX - downAt[0], e.clientY - downAt[1]));
    if (moved > 6) setFollow(false);
    ptrs.set(e.pointerId, { p: toSvg(e.clientX, e.clientY), cx: e.clientX, cy: e.clientY });
  } else if (ptrs.size === 2) {
    ptrs.set(e.pointerId, { p, cx: e.clientX, cy: e.clientY });
    const [a, b] = [...ptrs.values()];
    const d = Math.hypot(a.cx - b.cx, a.cy - b.cy);
    if (pinchDist) { const m = toSvg((a.cx + b.cx) / 2, (a.cy + b.cy) / 2); zoomAt(m.x, m.y, d / pinchDist); }
    pinchDist = d; moved = 99; setFollow(false);
  }
});
function endPointer(e) {
  if (!ptrs.has(e.pointerId)) return;
  ptrs.delete(e.pointerId);
  if (ptrs.size < 2) pinchDist = null;
  if (ptrs.size === 1) { const r = [...ptrs.values()][0]; r.p = toSvg(r.cx, r.cy); }
  if (ptrs.size === 0) {
    svg.classList.remove("dragging");
    if (moved <= 6 && e.type === "pointerup") {
      const hit = document.elementFromPoint(e.clientX, e.clientY);
      const g = hit && hit.closest("[data-organ]");
      if (g) showOrgan(g.dataset.organ);
    }
  }
}
svg.addEventListener("pointerup", endPointer);
svg.addEventListener("pointercancel", endPointer);
svg.addEventListener("wheel", (e) => {
  e.preventDefault(); camAnim = null;
  const p = toSvg(e.clientX, e.clientY);
  zoomAt(p.x, p.y, Math.exp(-e.deltaY * 0.0015));
}, { passive: false });
$("zoomIn").onclick = () => { camAnim = null; zoomAt(CX, CY, 1.3); };
$("zoomOut").onclick = () => { camAnim = null; zoomAt(CX, CY, 1 / 1.3); };
$("zoomReset").onclick = () => { setFollow(false); flyTo(WHOLE); };

// ---------- UI ----------
let toastTimer = null;
function toast(msg) {
  const t = $("toast"); t.textContent = msg; t.classList.add("show");
  clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.remove("show"), 2400);
}
function showOrgan(key) {
  const o = ORGANS[key]; if (!o) return;
  $("info").innerHTML = `<b>${o.name}</b><span class="crew">${o.crew}</span><br>${o.job}<br><i>Fun fact:</i> ${o.fact}`;
}
function setFollow(on) {
  if (state.follow === on) return;
  state.follow = on;
  $("followBtn").classList.toggle("on", on); $("followBtn").setAttribute("aria-pressed", on);
}
function setPressed(id, on) { $(id).classList.toggle("on", on); $(id).setAttribute("aria-pressed", on); }
$("followBtn").onclick = () => { setFollow(!state.follow); if (!state.follow) flyTo(dayView()); };
$("sprintBtn").onclick = () => {
  state.sprint = !state.sprint; setPressed("sprintBtn", state.sprint);
  $("sprintBtn").textContent = state.sprint ? "🛋️ Rest" : "🏃 Sprint!";
  toast(state.sprint ? "Sprinting! Heart and lungs speed up together." : "Resting. Everything slows back down.");
};
$("labelsBtn").onclick = () => { state.labels = !state.labels; updateLabels(); };
$("lightBtn").onclick = () => {
  const on = $("stageWrap").classList.toggle("light"); setPressed("lightBtn", on);
};

DAY_KEYS.forEach((k, i) => {
  const btn = document.createElement("button");
  btn.textContent = DAYS[k].tab; btn.style.background = DAYS[k].color; btn.dataset.day = k;
  btn.title = `Key ${i + 1}`; btn.onclick = () => selectDay(k);
  $("days").appendChild(btn);
});

for (const L of LABELS) {
  const g = mk("g", { class: "lbl", "data-for": L.for }, $("labels"));
  const left = L.side === "L", tx = left ? 92 : 508;
  mk("line", { x1: tx + (left ? 4 : -4), y1: L.y - 6, x2: L.t[0], y2: L.t[1] }, g);
  mk("circle", { cx: L.t[0], cy: L.t[1], r: 3.5 }, g);
  const t = mk("text", { x: tx, y: L.y, "text-anchor": left ? "end" : "start" }, g);
  t.textContent = L.text;
}
function updateLabels() {
  setPressed("labelsBtn", state.labels);
  const focus = DAYS[state.day].organs;
  document.querySelectorAll("#labels .lbl").forEach((g) => {
    const f = g.dataset.for;
    const show = state.labels && (state.day === "team" ? f !== "nerves" : focus.includes(f));
    g.setAttribute("opacity", show ? 1 : 0);
  });
}
function dayView() {
  const d = DAYS[state.day];
  if (!d.organs.length) return WHOLE;
  return viewFor(d.fit || d.organs, true);
}

const KEY_ITEMS = {
  cells: `<div><svg viewBox="-12 -12 24 24" width="34" height="34"><circle r="8" fill="#ef4444" stroke="#fecaca" stroke-width="1.5"/><circle cx="7" cy="-7" r="4.5" fill="#fff" stroke="#475569"/></svg>
    <span>Bright red + white bubble: carrying <b>oxygen</b></span></div>
    <div><svg viewBox="-12 -12 24 24" width="34" height="34"><circle r="8" fill="#7f1d1d" stroke="#fecaca" stroke-width="1.5"/><circle cx="7" cy="-7" r="4.5" fill="#9ca3af" stroke="#334155"/></svg>
    <span>Dark red + gray bubble: dropped off some oxygen, bringing <b>trash gas</b> back to the lungs. Never blue!</span></div>`,
  nerves: `<div><svg viewBox="0 0 24 24" width="34" height="34"><path d="M 2 12 L 22 12" stroke="#facc15" stroke-width="5" stroke-linecap="round"/></svg>
    <span>Yellow lines: <b>nerves</b> (they carry messages, not blood)</span></div>`,
};

function selectDay(key) {
  state.day = key; state.sceneT = 0; state.acc = {};
  const d = DAYS[key];
  document.documentElement.style.setProperty("--accent", d.color);
  document.querySelectorAll("#days button").forEach((b) => b.setAttribute("aria-pressed", b.dataset.day === key));
  document.querySelectorAll(".organ").forEach((g) => {
    const o = g.dataset.organ;
    g.classList.toggle("dim", d.organs.length > 0 && !d.organs.includes(o));
    if (o === "nerves") g.classList.toggle("hidden", key !== "fri");
  });
  $("dayTitle").textContent = d.title;
  $("rudySays").textContent = d.rudy;
  $("watch").innerHTML = d.watch.map((w) => `<li>${w}</li>`).join("");
  $("key").innerHTML = (["mon", "tue", "team"].includes(key) ? KEY_ITEMS.cells : "") + (key === "fri" ? KEY_ITEMS.nerves : "");
  cellsLayer.setAttribute("opacity", ["mon", "tue", "team"].includes(key) ? 1 : 0.3);
  $("breathText").setAttribute("opacity", 0);
  clearParticles(); bolus.setAttribute("opacity", 0); $("stomachInner").removeAttribute("transform");
  state.labels = key !== "team";
  buildExtra(key); updateLabels();
  setFollow(false); flyTo(dayView());
  if (location.hash !== "#" + key) history.replaceState(null, "", "#" + key);
}

// ---------- Particles ----------
const parts = [];
function spawn(o) {
  const c = mk("circle", { r: o.r || 4, fill: o.color || "#fff" }, fx);
  if (o.stroke) { c.setAttribute("stroke", o.stroke); c.setAttribute("stroke-width", 1); }
  if (o.glow) c.setAttribute("filter", "url(#glow)");
  const p = { ...o, el: c, t: 0, len: o.path ? o.path.getTotalLength() : 0 };
  parts.push(p); placePart(p, 0); return p;
}
function placePart(p, k) {
  let x, y;
  if (p.path) { const pt = p.path.getPointAtLength((p.rev ? 1 - k : k) * p.len); x = pt.x; y = pt.y; }
  else { x = p.from[0] + (p.to[0] - p.from[0]) * k; y = p.from[1] + (p.to[1] - p.from[1]) * k; }
  p.el.setAttribute("cx", x.toFixed(1)); p.el.setAttribute("cy", y.toFixed(1));
  if (p.colorFn) p.el.setAttribute("fill", p.colorFn(k));
  if (p.fade) p.el.setAttribute("opacity", (1 - k * k).toFixed(2));
  if (p.grow) p.el.setAttribute("r", ((p.r || 4) * (1 + p.grow * k)).toFixed(2));
  return [x, y];
}
function updateParticles(dt) {
  for (let i = parts.length - 1; i >= 0; i--) {
    const p = parts[i]; p.t += dt / p.dur;
    const k = Math.min(1, p.t); const [x, y] = placePart(p, k);
    if (k >= 1) { p.el.remove(); parts.splice(i, 1); if (p.then) p.then(x, y); }
  }
}
function clearParticles() { parts.forEach((p) => p.el.remove()); parts.length = 0; }
function every(name, secs, dt, fn) {
  state.acc[name] = (state.acc[name] || 0) + dt;
  while (state.acc[name] >= secs) { state.acc[name] -= secs; fn(); }
}
function mix(a, b, k) {
  const pa = [1, 3, 5].map((i) => parseInt(a.slice(i, i + 2), 16));
  const pb = [1, 3, 5].map((i) => parseInt(b.slice(i, i + 2), 16));
  return "rgb(" + pa.map((v, i) => Math.round(v + (pb[i] - v) * k)).join(",") + ")";
}

// ---------- Circulation: routes, drawn vessels, cells, Rudy ----------
// Every route starts and ends at the heart. Pulmonary routes leave the right side (312,410) and
// return to the left side (326,400); body routes leave the left side and return to the right.
const ROUTES = {
  pulmL: { kind: "pulm", turn: [238, 378], d: "M 312 410 C 290 402 258 396 246 384 C 234 372 238 358 252 360 C 268 364 300 390 326 400" },
  pulmR: { kind: "pulm", turn: [372, 380], d: "M 312 410 C 326 386 350 366 366 368 C 382 372 382 392 368 396 C 352 400 338 401 326 400" },
  head: { kind: "sys", w: 0.2, turn: [301, 124],
    d: "M 326 400 C 332 380 330 360 324 340 L 324 150 C 324 118 278 118 278 150 L 278 340 C 280 372 296 396 312 410" },
  armL: { kind: "sys", w: 0.15, turn: [144, 612],
    d: "M 326 400 C 328 376 320 362 310 356 L 198 300 L 136 598 C 132 618 152 620 154 604 L 210 314 L 300 366 C 306 386 308 400 312 410" },
  armR: { kind: "sys", w: 0.15, turn: [458, 612],
    d: "M 326 400 C 330 376 334 362 340 356 L 402 300 L 466 598 C 470 618 450 620 448 604 L 390 314 L 304 366 C 306 386 308 400 312 410" },
  legL: { kind: "sys", w: 0.25, turn: [250, 970],
    d: "M 326 400 C 324 430 318 450 318 470 L 314 690 L 268 722 L 258 958 C 256 976 240 976 242 958 L 252 725 L 290 690 L 288 470 C 290 440 300 420 312 410" },
  legR: { kind: "sys", w: 0.25, turn: [344, 970],
    d: "M 326 400 C 324 430 318 450 318 470 L 314 690 L 342 722 L 352 958 C 354 976 338 976 336 958 L 326 728 L 290 690 L 288 470 C 290 440 300 420 312 410" },
};
for (const [name, r] of Object.entries(ROUTES)) {
  r.el = mk("path", { d: r.d, id: "route-" + name }, $("routes"));
  r.len = r.el.getTotalLength();
  let best = 0, bd = Infinity;
  for (let l = 0; l <= r.len; l += 2) {
    const p = r.el.getPointAtLength(l); const d = (p.x - r.turn[0]) ** 2 + (p.y - r.turn[1]) ** 2;
    if (d < bd) { bd = d; best = l; }
  }
  r.turnAt = best;
}
const BRIGHT = "#ef4444", DARK = "#7f1d1d";
// Draw each route as two colours split at its turn point, so vessels show the loop and the U-turn.
function polyline(r, a, b) {
  const pts = [];
  for (let l = a; l < b; l += 3) { const p = r.el.getPointAtLength(l); pts.push(`${p.x.toFixed(1)},${p.y.toFixed(1)}`); }
  const p = r.el.getPointAtLength(b); pts.push(`${p.x.toFixed(1)},${p.y.toFixed(1)}`);
  return "M " + pts.join(" L ");
}
for (const r of Object.values(ROUTES)) {
  const parent = r.kind === "pulm" ? $("vesselsLung") : $("vesselsBody");
  const w = r.kind === "pulm" ? 4 : 5;
  const first = r.kind === "pulm" ? DARK : BRIGHT, second = r.kind === "pulm" ? BRIGHT : "#991b1b";
  mk("path", { d: polyline(r, 0, r.turnAt), stroke: first, "stroke-width": w }, parent);
  mk("path", { d: polyline(r, r.turnAt, r.len), stroke: second, "stroke-width": w }, parent);
  // capillary U-turn
  mk("path", { d: polyline(r, Math.max(0, r.turnAt - 14), Math.min(r.len, r.turnAt + 14)), stroke: "#c026d3",
    "stroke-width": 2.5, "stroke-dasharray": "2 2" }, parent);
}
const BODY_ROUTES = Object.entries(ROUTES).filter(([, r]) => r.kind === "sys");
function pickBody() {
  let x = Math.random();
  for (const [name, r] of BODY_ROUTES) { x -= r.w; if (x <= 0) return name; }
  return BODY_ROUTES[0][0];
}
const pickLung = () => (Math.random() < 0.55 ? "pulmL" : "pulmR");
// oxygenated: bright after the lungs' turn point, dark after a body route's U-turn
const isBright = (c) => (ROUTES[c.route].kind === "pulm" ? c.pos >= ROUTES[c.route].turnAt : c.pos < ROUTES[c.route].turnAt);

const N_CELLS = 28, cells = [];
function makeCell(rudy) {
  const g = mk("g", {}, rudy ? $("rudyLayer") : cellsLayer);
  if (rudy) {
    g.dataset.organ = "rudy"; g.style.cursor = "pointer";
    g.innerHTML = '<circle r="17" class="body" stroke="#fff" stroke-width="2.5" filter="url(#rudyGlow)"/>' +
      '<circle cx="-6" cy="-4" r="4" fill="#fff"/><circle cx="6" cy="-4" r="4" fill="#fff"/>' +
      '<circle cx="-6" cy="-4" r="1.9" fill="#111"/><circle cx="6" cy="-4" r="1.9" fill="#111"/>' +
      '<path d="M -6 6 Q 0 11 6 6" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round"/>' +
      '<g class="pack" transform="translate(17 -17)"><circle r="11" stroke="#334155" stroke-width="1.5"/>' +
      '<text text-anchor="middle" y="4" font-size="10" font-weight="bold" fill="#0f172a"></text></g>';
  } else {
    g.innerHTML = '<circle r="6" class="body" stroke="#fecaca" stroke-width="1.2"/>' +
      '<circle class="pack" cx="5.5" cy="-5.5" r="3" stroke="#334155" stroke-width=".8"/>';
  }
  return g;
}
for (let i = 0; i < N_CELLS; i++) {
  const rudy = i === 0;
  const route = rudy ? "pulmL" : i % 3 === 0 ? pickLung() : pickBody();
  const c = { el: makeCell(rudy), rudy, route, pos: rudy ? 0 : Math.random() * ROUTES[route].len, flips: [] };
  cells.push(c);
}
let rudyXY = [322, 415];
function speed() { return 70 * (state.bpm / 90); }  // length units per second
function updateBlood(dt) {
  const showFx = ["mon", "tue", "team"].includes(state.day);
  for (const c of cells) {
    const before = isBright(c);
    c.pos += speed() * dt;
    let r = ROUTES[c.route];
    if (c.pos >= r.len) {
      c.pos -= r.len;
      c.route = r.kind === "pulm" ? pickBody() : pickLung();
      r = ROUTES[c.route];
    }
    const p = r.el.getPointAtLength(c.pos);
    const bright = isBright(c);
    if (bright !== before) {
      c.flips.push({ route: c.route, at: c.pos, turnAt: r.turnAt });
      if (c.flips.length > 6) c.flips.shift();
      if (showFx || c.rudy) {
        if (bright) spawn({ from: [p.x, p.y], to: [p.x + 10, p.y - 40], dur: 1.2, r: 3.5, color: "#9ca3af", stroke: "#334155", fade: true });
        else spawn({ from: [p.x, p.y], to: [p.x + (Math.random() - 0.5) * 30, p.y - 18], dur: 1.0, r: 3.5, color: "#fff", stroke: "#334155", fade: true, grow: 0.6 });
      }
    }
    c.el.setAttribute("transform", `translate(${p.x.toFixed(1)} ${p.y.toFixed(1)})`);
    c.el.querySelector(".body").setAttribute("fill", bright ? BRIGHT : DARK);
    const pack = c.el.querySelector(".pack");
    if (c.rudy) {
      pack.querySelector("circle").setAttribute("fill", bright ? "#fff" : "#9ca3af");
      pack.querySelector("text").textContent = bright ? "O₂" : "CO₂";
      rudyXY = [p.x, p.y];
    } else pack.setAttribute("fill", bright ? "#fff" : "#9ca3af");
  }
  every("trail", 0.05, dt, () => spawn({ from: rudyXY, to: rudyXY, dur: 0.6, r: 7, color: "#fca5a5", fade: true }));
}

// ---------- Heart and breathing (always running) ----------
let lubDubShown = 0;
function onBeat() {
  if (state.day !== "tue") return;
  const t = mk("text", { class: "worldtext", x: 372, y: 392 }, fx);
  t.style.fontSize = "20px"; t.textContent = lubDubShown++ % 2 ? "dub!" : "lub-dub!";
  setTimeout(() => t.remove(), 450);
}
const bodyAnim = { heartScale: 1.45, lungScale: 1 };
function animateBody() {
  const b = state.beat, squeeze = b < 0.2 ? Math.sin((b / 0.2) * Math.PI) : 0;
  bodyAnim.heartScale = 1.45 * (1 - 0.1 * squeeze);
  $("heartInner").setAttribute("transform", `translate(322 415) rotate(-35) scale(${bodyAnim.heartScale.toFixed(3)})`);
  const inh = 0.5 - 0.5 * Math.cos(2 * Math.PI * state.breath);
  bodyAnim.lungScale = 1 + 0.075 * inh;
  $("lungsInner").setAttribute("transform",
    `translate(300 300) scale(${(1 + 0.045 * inh).toFixed(3)} ${bodyAnim.lungScale.toFixed(3)}) translate(-300 -300)`);
  $("diaphragmPath").setAttribute("d", `M 195 ${(482 + 10 * inh).toFixed(1)} Q 300 ${(430 + 34 * inh).toFixed(1)} 405 ${(482 + 10 * inh).toFixed(1)}`);
}

// ---------- Day scenes ----------
const bolus = mk("circle", { r: 9, stroke: "#451a03", "stroke-width": 1.5, opacity: 0 });
world.insertBefore(bolus, cellsLayer);
const PATHS = Object.fromEntries(["esoPath", "smallPath", "largePath", "airL", "airR", "renalL", "renalR",
  "ureterL", "ureterR", "portalPath", "eyePath", "earPath", "handPath", "legPath"].map((id) => [id, $(id)]));
const lenOf = Object.fromEntries(Object.entries(PATHS).map(([k, p]) => [k, p.getTotalLength()]));
const at = (id, k) => PATHS[id].getPointAtLength(Math.max(0, Math.min(1, k)) * lenOf[id]);

function sceneMon(dt) {
  const inhaling = state.breath < 0.5;
  const txt = $("breathText");
  txt.textContent = inhaling ? "Breathe in!" : "Breathe out!";
  txt.setAttribute("opacity", 1);
  every("air", 0.12 * (20 / state.brpm), dt, () => {
    const side = Math.random() < 0.5 ? "airL" : "airR";
    const dur = 1.8 * (20 / state.brpm);
    if (inhaling) spawn({ path: PATHS[side], dur, r: 4, color: "#e0f2fe", stroke: "#0369a1" });
    else spawn({ path: PATHS[side], rev: true, dur, r: 4, color: "#9ca3af", stroke: "#334155" });
  });
}

function sceneWed(dt) {
  const CYCLE = 11, k = (state.sceneT % CYCLE) / CYCLE;
  bolus.setAttribute("opacity", 1);
  const stomach = $("stomachInner");
  let p, col = "#92400e", r = 9;
  if (k < 0.16) { p = at("esoPath", k / 0.16); stomach.removeAttribute("transform"); }
  else if (k < 0.42) {
    const w = Math.sin(state.sceneT * 9) * 0.05;
    stomach.setAttribute("transform", `translate(356 548) scale(${1 + w} ${1 - w}) translate(-356 -548)`);
    const j = (k - 0.16) / 0.26;
    p = { x: 352 + 18 * Math.sin(state.sceneT * 7) * (1 - j), y: 550 + 10 * Math.cos(state.sceneT * 5) * (1 - j) + 22 * j };
    col = mix("#92400e", "#d97706", j); r = 9 + 2 * j;
  } else if (k < 0.8) {
    stomach.removeAttribute("transform");
    const j = (k - 0.42) / 0.38; p = at("smallPath", j); col = "#d97706"; r = 10 - 4 * j;
    every("nutrient", 0.14, dt, () => spawn({ from: [p.x, p.y], to: [314, p.y - 20], dur: 0.9, r: 3.5, color: "#facc15", fade: true, glow: true }));
  } else if (k < 0.97) {
    const j = (k - 0.8) / 0.17; p = at("largePath", j); col = mix("#d97706", "#78350f", j); r = 6;
    every("water", 0.16, dt, () => spawn({ from: [p.x, p.y], to: [p.x + (Math.random() - 0.5) * 50, p.y - 25], dur: 0.8, r: 3, color: "#38bdf8", fade: true }));
  } else { p = at("largePath", 1); bolus.setAttribute("opacity", 0); }
  bolus.setAttribute("cx", p.x.toFixed(1)); bolus.setAttribute("cy", p.y.toFixed(1));
  bolus.setAttribute("r", r.toFixed(1)); bolus.setAttribute("fill", col);
}

function urineColor() { return mix("#ca8a04", "#fef08a", state.hydration); }
function sceneThu(dt) {
  state.hydration = Math.max(0, state.hydration - dt * 0.025);
  const h = 36 * Math.min(1, state.bladder), bf = $("bladderFill");
  bf.setAttribute("y", (726 - h).toFixed(1)); bf.setAttribute("height", h.toFixed(1)); bf.setAttribute("fill", urineColor());
  const m = $("hydroMeter"); if (m) m.style.width = Math.round(state.hydration * 100) + "%";
  every("waste", 0.45, dt, () => {
    const side = Math.random() < 0.5 ? "L" : "R";
    spawn({ path: PATHS["renal" + side], dur: 0.5, r: 3.5, color: "#64748b", then: () => {
      spawn({ path: PATHS["ureter" + side], dur: 1.3, r: 3, color: urineColor(), then: () => {
        state.bladder += 0.035 * (0.6 + state.hydration);
        if (state.bladder >= 1) { state.bladder = 0.05; toast("Bladder full! Bathroom break! 🚽"); }
      } });
    } });
  });
  every("liver", 0.7, dt, () => spawn({ path: PATHS.portalPath, dur: 1.2, r: 3.5, color: "#64748b", then: (x, y) =>
    spawn({ from: [x, y], to: [x - 10 + Math.random() * 20, y - 12], dur: 0.6, r: 3, color: "#4ade80", fade: true, grow: 1.5, glow: true }) }));
}

function brainFlash() {
  const b = $("brainShape"); b.setAttribute("fill", "#fde047");
  setTimeout(() => b.setAttribute("fill", "#f9a8d4"), 220);
}
function signal(inPath, outPath) {
  spawn({ path: PATHS[inPath], dur: 0.35, r: 6, color: "#fde047", glow: true, then: () => {
    brainFlash();
    spawn({ path: PATHS[outPath], dur: 0.6, r: 6, color: "#fde047", glow: true });
  } });
}
function sceneFri(dt) {
  every("signal", 1.7, dt, () => (Math.random() < 0.5 ? signal("eyePath", "handPath") : signal("earPath", "legPath")));
}

// ---------- Panel extras (Thursday water, Friday ruler drop) ----------
const game = { mode: "idle", t0: 0, timer: null, tries: [] };
function buildExtra(key) {
  const ex = $("extra"); ex.innerHTML = ""; clearTimeout(game.timer); game.mode = "idle";
  if (key === "thu") {
    ex.innerHTML = '<button id="drinkBtn">💧 Drink water</button>' +
      '<div>Water in your body:</div><div class="meter"><div id="hydroMeter"></div></div>' +
      '<div>Pale yellow pee = plenty of water. Dark yellow = drink up!</div>';
    $("drinkBtn").onclick = () => { state.hydration = Math.min(1, state.hydration + 0.35); toast("Glug, glug! 💧 More water to wash the waste away."); };
  }
  if (key === "fri") {
    const marks = [0, 5, 10, 15, 20, 25, 30].map((cm) => `<span style="bottom:${cm * 6}px">${cm}</span>`).join("");
    ex.innerHTML = '<div class="game"><b>Ruler Drop</b>' +
      `<div class="ruler-box" id="rulerBox"><div class="ruler" id="ruler">${marks}</div><div class="hand">✋</div></div>` +
      '<button id="gameBtn">Start</button><div id="gameMsg">Press Start. When the ruler drops, tap Catch (or press the space bar) as fast as you can!</div>' +
      '<ol id="tries"></ol></div>';
    $("gameBtn").onclick = gamePress; $("rulerBox").onpointerdown = () => { if (game.mode !== "idle") gamePress(); };
    renderTries();
  }
}
function setRuler(cm) { const r = $("ruler"); if (r) r.style.transform = `translateY(${(cm * 6).toFixed(1)}px)`; }
function renderTries() { const el = $("tries"); if (el) el.innerHTML = game.tries.map((t) => `<li>${t}</li>`).join(""); }
function gamePress() {
  const btn = $("gameBtn"), msg = $("gameMsg");
  if (game.mode === "idle") {
    setRuler(0); game.mode = "waiting"; btn.textContent = "Catch!"; msg.textContent = "Get ready... watch the ruler!";
    game.timer = setTimeout(() => { game.mode = "dropping"; game.t0 = performance.now(); }, 1200 + Math.random() * 2500);
  } else if (game.mode === "waiting") {
    clearTimeout(game.timer); game.mode = "idle"; btn.textContent = "Start"; msg.textContent = "Too soon! Wait until the ruler starts to fall.";
  } else if (game.mode === "dropping") {
    const t = (performance.now() - game.t0) / 1000, cm = 490.5 * t * t;
    game.mode = "idle"; btn.textContent = "Again";
    msg.innerHTML = `Caught at <b>${cm.toFixed(0)} centimeters</b>! Your brain took ${t.toFixed(2)} seconds.`;
    game.tries.push(`${cm.toFixed(0)} cm (${t.toFixed(2)} s)`); if (game.tries.length > 5) game.tries.shift();
    renderTries(); signal("eyePath", "handPath");
  }
}
function updateGame() {
  if (game.mode !== "dropping") return;
  const t = (performance.now() - game.t0) / 1000, cm = 490.5 * t * t;
  if (cm > 30) {
    game.mode = "idle"; setRuler(45); $("gameBtn").textContent = "Again";
    $("gameMsg").textContent = "Missed! It fell past 30 cm. Try again!";
    game.tries.push("missed (more than 30 cm)"); if (game.tries.length > 5) game.tries.shift(); renderTries();
  } else setRuler(cm);
}

// ---------- Keyboard ----------
document.addEventListener("keydown", (e) => {
  if (e.target.tagName === "BUTTON" && (e.key === " " || e.key === "Enter")) return;
  const n = parseInt(e.key, 10);
  if (n >= 1 && n <= 6) { selectDay(DAY_KEYS[n - 1]); return; }
  const step = 40;
  if (e.key === "ArrowLeft") cam.x += step; else if (e.key === "ArrowRight") cam.x -= step;
  else if (e.key === "ArrowUp") cam.y += step; else if (e.key === "ArrowDown") cam.y -= step;
  else if (e.key === "+" || e.key === "=") zoomAt(CX, CY, 1.25);
  else if (e.key === "-") zoomAt(CX, CY, 0.8);
  else if (e.key === " " && state.day === "fri") { e.preventDefault(); gamePress(); return; }
  else return;
  camAnim = null; setFollow(false); applyCam();
});

// ---------- Main loop ----------
let last = performance.now();
function frame(now) {
  const dt = Math.min(0.05, (now - last) / 1000); last = now; state.sceneT += dt;
  const tb = state.sprint ? 150 : 90, tr = state.sprint ? 40 : 20, ease = Math.min(1, dt * 1.2);
  state.bpm += (tb - state.bpm) * ease; state.brpm += (tr - state.brpm) * ease;
  const prevBeat = state.beat;
  state.beat = (state.beat + dt * state.bpm / 60) % 1; if (state.beat < prevBeat) onBeat();
  state.breath = (state.breath + dt * state.brpm / 60) % 1;
  animateBody(); updateBlood(dt);
  if (state.day === "mon") sceneMon(dt);
  else if (state.day === "wed") sceneWed(dt);
  else if (state.day === "thu") sceneThu(dt);
  else if (state.day === "fri") sceneFri(dt);
  updateParticles(dt); updateGame();
  if (state.follow) {
    camAnim = null;
    const s = 3, tx = CX - s * rudyXY[0], ty = CY - s * rudyXY[1], k = Math.min(1, dt * 4);
    cam.s += (s - cam.s) * k; cam.x += (tx - cam.x) * k; cam.y += (ty - cam.y) * k; applyCam();
  } else if (camAnim) {
    const j = Math.min(1, (now - camAnim.t0) / camAnim.ms), e = j < 0.5 ? 2 * j * j : 1 - (-2 * j + 2) ** 2 / 2;
    for (const key of ["x", "y", "s"]) cam[key] = camAnim.from[key] + (camAnim.to[key] - camAnim.from[key]) * e;
    applyCam(); if (j >= 1) camAnim = null;
  }
  $("readout").textContent = `♥ ${Math.round(state.bpm)} beats/min · 🫁 ${Math.round(state.brpm)} breaths/min`;
  requestAnimationFrame(frame);
}

// The whole body fills the height; labels sit in the side columns.
WHOLE = fitBox({ x: 90, y: 26, width: 420, height: 955 });
applyCam();
// Read-only hook for automated checks (cell colour flips, heart/lung timing).
window.__explorer = { state, cells, ROUTES, bodyAnim };
const startDay = location.hash.slice(1);
selectDay(DAY_KEYS.includes(startDay) ? startDay : "team");
window.addEventListener("hashchange", () => {
  const k = location.hash.slice(1);
  if (DAY_KEYS.includes(k) && k !== state.day) selectDay(k);
});
toast("Drag to look around. Scroll or pinch to zoom!");
requestAnimationFrame(frame);
</script>
</body>
</html>
"""


def build_html() -> str:
    return EXPLORER_HTML
