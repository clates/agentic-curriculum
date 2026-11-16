"""
Body Explorer — the interactive companion to the Body Team Week packet.

``build_html()`` returns one self-contained HTML file (inline SVG + JS, no network, no
dependencies). A simplified front-view body the student can pan and zoom, with one scene per
day of the week — lungs, heart, digestion, liver and kidneys, brain — plus a Whole Team view.
Rudy the Red Blood Cell rides the bloodstream the whole time, and the Sprint toggle speeds the
heart, breathing and Rudy together.

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
  svg#stage { width: 100%; height: 100%; display: block; touch-action: none; cursor: grab; user-select: none; }
  svg#stage.dragging { cursor: grabbing; }
  button { font: inherit; font-weight: bold; border: none; border-radius: 10px; padding: 8px 12px;
    cursor: pointer; background: #fff; color: #0f172a; box-shadow: 0 2px 6px rgba(0,0,0,.35); }
  button:focus-visible { outline: 3px solid #fde047; outline-offset: 2px; }
  .days { position: absolute; top: 10px; left: 10px; right: 10px; display: flex; flex-wrap: wrap; gap: 6px; }
  .days button { color: #fff; }
  .days button[aria-pressed="true"] { outline: 3px solid #fde047; outline-offset: 1px; transform: translateY(1px); }
  .zoom { position: absolute; right: 10px; bottom: 10px; display: flex; flex-direction: column; gap: 6px; }
  .zoom button { width: 46px; height: 46px; font-size: 20px; padding: 0; }
  .toggles { position: absolute; left: 10px; bottom: 54px; display: flex; flex-wrap: wrap; gap: 6px; }
  .toggles button.on { background: #fde047; }
  .readout { position: absolute; left: 10px; bottom: 10px; background: rgba(255,255,255,.92);
    border-radius: 10px; padding: 7px 11px; font-size: 14px; font-weight: bold; }
  .toast { position: absolute; top: 64px; left: 50%; transform: translateX(-50%); background: #fde047;
    padding: 8px 16px; border-radius: 999px; font-weight: bold; opacity: 0; transition: opacity .35s;
    pointer-events: none; white-space: nowrap; box-shadow: 0 2px 8px rgba(0,0,0,.4); }
  .toast.show { opacity: 1; }
  .panel { width: 370px; background: #fff; overflow-y: auto; padding: 16px 18px 24px;
    border-left: 6px solid var(--accent); }
  .panel h1 { font-size: 13px; margin: 0 0 4px; color: #64748b; text-transform: uppercase; letter-spacing: .08em; }
  .panel h2 { font-size: 22px; margin: 0 0 6px; color: var(--accent); }
  .panel h3 { font-size: 13px; text-transform: uppercase; letter-spacing: .06em; color: #475569; margin: 16px 0 6px; }
  .rudy-says { display: flex; gap: 10px; align-items: flex-start; margin: 10px 0; }
  .rudy-says svg { flex: 0 0 48px; }
  .bubble { background: #fee2e2; border-radius: 12px; padding: 8px 12px; font-size: 15px; line-height: 1.4; }
  .panel ul { padding-left: 20px; margin: 0; font-size: 15px; line-height: 1.45; }
  .panel li { margin-bottom: 4px; }
  .card { border: 2px solid #e2e8f0; border-radius: 12px; padding: 10px 12px; font-size: 15px; line-height: 1.45; }
  .card b { color: var(--accent); font-size: 17px; }
  .card .crew { display: inline-block; font-size: 12px; font-weight: bold; color: #fff; background: var(--accent);
    border-radius: 999px; padding: 1px 8px; margin-left: 6px; vertical-align: 2px; }
  .legend { font-size: 13px; color: #475569; line-height: 1.6; margin-top: 10px; }
  .dot { display: inline-block; width: 12px; height: 12px; border-radius: 50%; vertical-align: -1px; margin-right: 4px; }
  .extra { margin-top: 12px; }
  .meter { height: 14px; border-radius: 7px; background: #e2e8f0; overflow: hidden; margin: 6px 0; }
  .meter > div { height: 100%; background: #38bdf8; transition: width .3s; }
  .game { border: 2px dashed #94a3b8; border-radius: 12px; padding: 10px; text-align: center; }
  .ruler-box { position: relative; height: 330px; width: 140px; margin: 6px auto; overflow: hidden; }
  .ruler { position: absolute; left: 50px; top: 0; width: 38px; height: 180px; border: 2px solid #92400e;
    border-radius: 3px; background: repeating-linear-gradient(to top, #fde68a 0 5px, #b45309 5px 6px); }
  .ruler span { position: absolute; left: 3px; font-size: 11px; font-weight: bold; color: #451a03;
    background: #fde68a; padding: 0 2px; transform: translateY(50%); }
  .hand { position: absolute; left: 44px; top: 162px; font-size: 42px; line-height: 1; pointer-events: none; }
  #gameMsg { font-size: 15px; min-height: 42px; margin: 6px 0; }
  #tries { text-align: left; font-size: 14px; }
  .organ { transition: opacity .5s; }
  .organ.dim { opacity: .16; }
  .label { font-size: 15px; font-weight: bold; fill: #fff; paint-order: stroke; stroke: #0f172a; stroke-width: 4px;
    stroke-linejoin: round; pointer-events: none; transition: opacity .4s; }
  .worldtext { font-size: 22px; font-weight: bold; fill: #fde047; paint-order: stroke; stroke: #0f172a;
    stroke-width: 5px; pointer-events: none; }
  @media (max-width: 820px) {
    button { font-size: 13px; padding: 6px 9px; border-radius: 8px; }
    .zoom button { width: 38px; height: 38px; font-size: 18px; }
    .toggles { right: 58px; bottom: 46px; }
    .readout { font-size: 12px; padding: 5px 8px; }
    .app { flex-direction: column; height: auto; }
    .stage-wrap { height: 64vh; flex: none; }
    .panel { width: auto; border-left: none; border-top: 6px solid var(--accent); }
  }
</style>
</head>
<body>
<div class="app">
<div class="stage-wrap">
<svg id="stage" viewBox="0 0 600 1000" preserveAspectRatio="xMidYMid meet" role="img"
     aria-label="A simplified human body. Drag to look around, scroll or pinch to zoom, tap an organ to learn its job.">
  <defs>
    <filter id="glow" x="-1" y="-1" width="3" height="3">
      <feGaussianBlur stdDeviation="2.5" result="b"/>
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
      <path d="M 296 140 Q 300 150 304 140" fill="none" stroke="#c08a68" stroke-width="2.5" stroke-linecap="round"/>
      <path d="M 284 165 Q 300 175 316 165" fill="none" stroke="#b45309" stroke-width="3" stroke-linecap="round"/>
    </g>

    <!-- Nerves: brain to every part of the body -->
    <g class="organ" data-organ="nerves">
      <g stroke="#facc15" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path d="M 300 150 L 300 690"/>
        <path d="M 300 280 L 205 300 L 140 600"/>
        <path d="M 300 280 L 395 300 L 460 600"/>
        <path d="M 300 690 L 262 720 L 252 960"/>
        <path d="M 300 690 L 338 720 L 348 960"/>
        <path d="M 300 420 L 230 450"/><path d="M 300 420 L 370 450"/>
        <path d="M 300 560 L 240 590"/><path d="M 300 560 L 360 590"/>
      </g>
    </g>

    <!-- Blood vessels: arteries (bright red) and veins (dark red) -->
    <g class="organ" data-organ="vessels" fill="none" stroke-linecap="round" stroke-linejoin="round">
      <g stroke="#991b1b" stroke-width="5">
        <path d="M 300 400 L 288 470 L 290 690"/>
        <path d="M 290 690 L 252 725 L 242 960"/>
        <path d="M 290 690 L 326 728 L 336 962"/>
        <path d="M 296 382 L 290 200 L 290 135"/>
        <path d="M 298 362 L 208 312 L 150 605"/>
        <path d="M 304 362 L 392 312 L 450 605"/>
      </g>
      <g stroke="#ef4444" stroke-width="5">
        <path d="M 312 392 C 306 350 344 345 338 380 L 318 470 L 314 690"/>
        <path d="M 314 690 L 268 722 L 258 960"/>
        <path d="M 314 690 L 342 722 L 352 960"/>
        <path d="M 322 360 L 312 200 L 312 135"/>
        <path d="M 316 356 L 198 300 L 138 600"/>
        <path d="M 330 356 L 402 300 L 464 600"/>
        <path id="renalL" d="M 314 560 L 258 576"/>
        <path id="renalR" d="M 314 560 L 343 576"/>
      </g>
    </g>

    <!-- Kidneys sit in the back, behind the gut: dashed outline -->
    <g class="organ" data-organ="kidneys">
      <path d="M 245 545 C 230 545 222 560 222 578 C 222 598 232 610 247 610 C 258 610 262 600 256 590 C 252 582 252 572 256 565 C 262 555 258 545 245 545 Z"
            fill="#be123c" stroke="#881337" stroke-width="3" stroke-dasharray="6 3"/>
      <path d="M 355 545 C 370 545 378 560 378 578 C 378 598 368 610 353 610 C 342 610 338 600 344 590 C 348 582 348 572 344 565 C 338 555 342 545 355 545 Z"
            fill="#be123c" stroke="#881337" stroke-width="3" stroke-dasharray="6 3"/>
      <path id="ureterL" d="M 254 598 C 262 640 280 680 292 700" fill="none" stroke="#eab308" stroke-width="4"/>
      <path id="ureterR" d="M 346 598 C 338 640 320 680 308 700" fill="none" stroke="#eab308" stroke-width="4"/>
    </g>

    <!-- Esophagus: behind the windpipe, lungs and heart -->
    <g class="organ" data-organ="esophagus">
      <path id="esoPath" d="M 304 182 L 306 200 L 308 300 C 310 380 312 440 318 470 C 322 490 335 505 345 515"
            fill="none" stroke="#c98b63" stroke-width="10" stroke-linecap="round"/>
    </g>

    <!-- Liver (body's right = viewer's left) with the gallbladder -->
    <g class="organ" data-organ="liver">
      <path d="M 200 492 C 230 480 300 480 330 492 C 335 505 322 520 300 528 C 270 545 230 560 210 552 C 198 540 196 510 200 492 Z"
            fill="#9a3412" stroke="#7c2d12" stroke-width="3"/>
      <ellipse cx="270" cy="540" rx="9" ry="6" fill="#65a30d" stroke="#3f6212" stroke-width="2"/>
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
      <path id="largePath" d="M 250 690 C 236 690 232 670 232 650 L 232 615 C 232 602 240 597 255 597 L 345 597 C 360 597 368 602 368 615 L 368 655 C 368 680 350 690 330 690 C 318 690 312 700 310 712"
            fill="none" stroke="#b45309" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M 250 690 C 236 690 232 670 232 650 L 232 615 C 232 602 240 597 255 597 L 345 597 C 360 597 368 602 368 615 L 368 655 C 368 680 350 690 330 690 C 318 690 312 700 310 712"
            fill="none" stroke="#f59e0b" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>
    </g>

    <!-- Small intestine: the long coiled tube -->
    <g class="organ" data-organ="smallInt">
      <path d="M 310 578 C 290 590 262 605 262 615 C 262 628 338 622 338 636 C 338 650 262 644 262 658 C 262 672 338 666 338 680 C 338 690 300 690 280 688 C 268 687 258 690 250 690"
            fill="none" stroke="#be185d" stroke-width="13" stroke-linecap="round"/>
      <path id="smallPath" d="M 310 578 C 290 590 262 605 262 615 C 262 628 338 622 338 636 C 338 650 262 644 262 658 C 262 672 338 666 338 680 C 338 690 300 690 280 688 C 268 687 258 690 250 690"
            fill="none" stroke="#f9a8d4" stroke-width="8" stroke-linecap="round"/>
    </g>

    <!-- Bladder, with a fill level clipped to its shape -->
    <g class="organ" data-organ="bladder">
      <ellipse cx="300" cy="708" rx="26" ry="18" fill="#fffbeb"/>
      <rect id="bladderFill" x="270" y="726" width="60" height="0" fill="#fde047" clip-path="url(#bladderClip)"/>
      <ellipse cx="300" cy="708" rx="26" ry="18" fill="none" stroke="#ca8a04" stroke-width="3"/>
    </g>

    <!-- Windpipe and bronchi -->
    <g class="organ" data-organ="windpipe">
      <path d="M 300 190 L 300 300" stroke="#93c5fd" stroke-width="13" stroke-linecap="round"/>
      <g stroke="#60a5fa" stroke-width="2">
        <line x1="294" y1="210" x2="306" y2="210"/><line x1="294" y1="230" x2="306" y2="230"/>
        <line x1="294" y1="250" x2="306" y2="250"/><line x1="294" y1="270" x2="306" y2="270"/>
      </g>
      <path d="M 300 300 Q 280 310 262 332 M 300 300 Q 320 310 338 332" fill="none" stroke="#93c5fd" stroke-width="9" stroke-linecap="round"/>
    </g>

    <!-- Lungs: body's right lung (viewer's left) is bigger; the left lung has a notch for the heart -->
    <g class="organ" data-organ="lungs">
      <g id="lungsInner">
        <path d="M 288 300 C 260 285 215 300 205 350 C 195 400 198 450 205 470 C 235 480 270 475 290 465 C 292 420 292 360 288 300 Z"
              fill="#fda4af" fill-opacity=".92" stroke="#e11d48" stroke-width="3"/>
        <path d="M 312 300 C 340 285 385 300 395 350 C 403 400 402 450 395 468 C 375 475 360 474 352 470 C 350 450 335 440 325 430 C 315 410 314 360 312 300 Z"
              fill="#fda4af" fill-opacity=".92" stroke="#e11d48" stroke-width="3"/>
        <g fill="none" stroke="#e11d48" stroke-width="1.6" opacity=".7">
          <path d="M 212 380 L 286 360"/><path d="M 210 430 L 288 420"/><path d="M 392 372 L 318 400"/>
          <path d="M 262 332 L 250 360 L 236 380 M 250 360 L 258 400 L 248 440 M 258 400 L 272 430"/>
          <path d="M 338 332 L 352 360 L 368 380 M 352 360 L 350 400 L 362 440 M 350 400 L 380 420"/>
        </g>
        <g fill="#fecdd3" stroke="#e11d48" stroke-width="1">
          <circle cx="236" cy="384" r="4"/><circle cx="243" cy="387" r="4"/><circle cx="238" cy="391" r="4"/>
          <circle cx="248" cy="444" r="4"/><circle cx="255" cy="446" r="4"/><circle cx="250" cy="451" r="4"/>
          <circle cx="368" cy="384" r="4"/><circle cx="375" cy="386" r="4"/><circle cx="370" cy="391" r="4"/>
          <circle cx="362" cy="444" r="4"/><circle cx="369" cy="446" r="4"/><circle cx="364" cy="451" r="4"/>
        </g>
      </g>
      <path id="airL" d="M 300 150 L 300 300 L 262 332 L 250 360 L 238 388" fill="none" stroke="none"/>
      <path id="airR" d="M 300 150 L 300 300 L 338 332 L 352 360 L 369 388" fill="none" stroke="none"/>
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

    <!-- Brain and brain stem -->
    <g class="organ" data-organ="brain">
      <rect x="294" y="126" width="12" height="54" rx="6" fill="#f9a8d4" fill-opacity=".35" stroke="#be185d" stroke-width="1.5" stroke-dasharray="4 3" stroke-opacity=".6"/>
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
      <ellipse cx="276" cy="128" rx="10" ry="7" fill="#fff" stroke="#334155" stroke-width="2"/>
      <ellipse cx="324" cy="128" rx="10" ry="7" fill="#fff" stroke="#334155" stroke-width="2"/>
      <circle cx="276" cy="128" r="4" fill="#1e3a8a"/><circle cx="324" cy="128" r="4" fill="#1e3a8a"/>
      <ellipse cx="229" cy="118" rx="10" ry="18" fill="#f2c4a6" stroke="#c08a68" stroke-width="2.5"/>
      <ellipse cx="371" cy="118" rx="10" ry="18" fill="#f2c4a6" stroke="#c08a68" stroke-width="2.5"/>
      <path id="eyePath" d="M 276 128 C 283 112 292 100 300 92" fill="none" stroke="none"/>
      <path id="earPath" d="M 371 118 C 355 108 335 100 305 92" fill="none" stroke="none"/>
      <path id="handPath" d="M 300 100 L 300 280 L 205 300 L 140 600" fill="none" stroke="none"/>
      <path id="legPath" d="M 300 100 L 300 690 L 262 720 L 252 960" fill="none" stroke="none"/>
    </g>

    <!-- Rudy's loop: lungs, heart, up to the brain, back, down to the legs, back -->
    <path id="loopPath" fill="none" stroke="none"
          d="M 322 415 C 290 405 245 395 240 360 C 236 330 270 320 290 340 C 300 352 308 380 318 400 C 330 380 336 340 318 300 C 312 260 314 200 312 140 C 311 120 296 120 296 140 L 292 300 C 292 340 298 380 318 410 C 316 480 314 560 314 690 C 300 760 262 820 252 940 C 250 955 238 955 238 940 C 245 820 270 760 290 690 C 290 600 292 480 322 415 Z"/>
    <g id="cells"></g>
    <g id="fx" style="pointer-events:none"></g>
    <g id="labels"></g>
    <text id="breathText" class="worldtext" x="232" y="268" text-anchor="middle" opacity="0"></text>
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
    <svg viewBox="-13 -13 26 26" width="48" height="48" aria-hidden="true">
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
  <div class="legend" id="legend">
    <span class="dot" style="background:#ef4444"></span>Bright red: loaded with oxygen<br>
    <span class="dot" style="background:#7f1d1d"></span>Dark red: oxygen dropped off (blood is never blue!)
  </div>
  <h3>Tap an organ</h3>
  <div class="card" id="info">Tap any organ, or Rudy himself, to see its job.</div>
  <p class="legend">Drag to look around. Scroll or pinch to zoom. Keys: 1–5 for Monday–Friday, 6 for the
    whole team, arrows to pan.<br>A simplified model: real organs overlap and sit at different depths.
    The kidneys (dashed) are in your back.</p>
</aside>
</div>

<script>
"use strict";
const NS = "http://www.w3.org/2000/svg";
const $ = (id) => document.getElementById(id);
const svg = $("stage"), world = $("world"), fx = $("fx"), cellsLayer = $("cells");

const ORGANS = {
  lungs: { name: "Lungs", crew: "Air Crew", job: "Load oxygen into the blood and send carbon dioxide out.",
    fact: "Your left lung is a little smaller, to leave room for your heart.", at: [232, 425] },
  windpipe: { name: "Windpipe", crew: "Air Crew", job: "Carries air from your throat down to your lungs.",
    fact: "It splits into smaller and smaller tubes, like an upside-down tree.", at: [348, 262], anchor: "start" },
  diaphragm: { name: "Diaphragm", crew: "Air Crew", job: "Pulls DOWN so air rushes into your lungs.",
    fact: "Hiccups happen when your diaphragm twitches!", at: [372, 470] },
  heart: { name: "Heart", crew: "Pump Crew", job: "Pumps blood all over your body.",
    fact: "It is about the size of your fist, and it never takes a day off.", at: [338, 452] },
  vessels: { name: "Arteries & Veins", crew: "Pump Crew",
    job: "Arteries carry blood AWAY from the heart. Veins bring it BACK.",
    fact: "Blood is always red. Veins only look blue through your skin.", at: [300, 860] },
  esophagus: { name: "Esophagus", crew: "Fuel Crew", job: "Squeezes food down from your throat to your stomach.",
    fact: "It squeezes so well that astronauts can swallow upside down in space.", at: [322, 218], anchor: "start" },
  stomach: { name: "Stomach", crew: "Fuel Crew", job: "Churns food with acid into a thick soup.",
    fact: "A slimy lining keeps the acid from hurting the stomach itself.", at: [372, 552] },
  smallInt: { name: "Small intestine", crew: "Fuel Crew", job: "Soaks nutrients from food into the blood.",
    fact: "A grown-up's is about 20 feet long, all coiled up in the belly.", at: [300, 652] },
  largeInt: { name: "Large intestine", crew: "Fuel Crew", job: "Soaks up leftover water. Waste leaves the body.",
    fact: "It is shorter than the small intestine, but wider.", at: [300, 592] },
  liver: { name: "Liver", crew: "Clean-Up Crew", job: "Cleans harmful stuff out of the blood, stores fuel, and makes bile.",
    fact: "It is the biggest organ inside your body, and it can grow back! The little green bag is the gallbladder, where bile waits.",
    at: [248, 512] },
  kidneys: { name: "Kidneys", crew: "Clean-Up Crew", job: "Filter waste and extra water out of the blood to make urine.",
    fact: "They sit in your back, one on each side of your spine.", at: [300, 548] },
  bladder: { name: "Bladder", crew: "Clean-Up Crew", job: "Holds urine until you go to the bathroom.",
    fact: "It stretches like a balloon as it fills.", at: [300, 752] },
  brain: { name: "Brain", crew: "Coaching Staff",
    job: "The Head Coach: gets messages from your senses and tells your body what to do.",
    fact: "It uses about one fifth of all the oxygen Rudy carries. The brain stem keeps you breathing, even asleep.",
    at: [300, 30] },
  nerves: { name: "Spinal cord & nerves", crew: "Coaching Staff",
    job: "Carry messages between your brain and your body.",
    fact: "Messages zip along some nerves faster than a race car.", at: [150, 660] },
  senses: { name: "Eyes & ears", crew: "Coaching Staff", job: "Send messages about the world IN to your brain.",
    fact: "Your eyes collect light, but it's your brain that figures out what you're seeing.",
    at: [386, 122], anchor: "start" },
  rudy: { name: "Rudy the Red Blood Cell", crew: "Delivery Truck",
    job: "Carries oxygen from the lungs to every cell in your body.",
    fact: "Bright red means he's loaded with oxygen. Dark red means he just dropped it off." },
};

const DAYS = {
  mon: { tab: "Mon · Lungs", color: "#1d4ed8", title: "Monday · Breathe In!", organs: ["lungs", "windpipe", "diaphragm"],
    rudy: "This is my first stop! I park by the tiny air sacs and load up on oxygen.",
    watch: ["Watch the orange diaphragm pull DOWN: air rushes IN.",
      "Dark-red cells turn bright red in the lungs. That's oxygen getting loaded!",
      "Blue dots are fresh air coming in. Gray dots are carbon dioxide going out.",
      "Tap Sprint and watch the breathing speed up."] },
  tue: { tab: "Tue · Heart", color: "#15803d", title: "Tuesday · The Pump", organs: ["heart", "vessels"], fit: ["heart", "lungs"],
    rudy: "The heart is my engine! The right side sends me to the lungs. The left side blasts me out to the body.",
    watch: ["Every squeeze is one heartbeat: lub-dub!",
      "Bright red blood goes OUT through the arteries. Darker red comes BACK in the veins.",
      "Tap Sprint: the heart AND the lungs speed up together. Teamwork!"] },
  wed: { tab: "Wed · Digestion", color: "#7c3aed", title: "Wednesday · The Fuel Factory",
    organs: ["esophagus", "stomach", "smallInt", "largeInt"],
    rudy: "Food fuel doesn't ride on me. It floats in the blood river all around me!",
    watch: ["Follow the brown food bite: mouth, esophagus, stomach.",
      "The stomach churns it into a thick soup.",
      "Yellow nutrients soak into the blood in the small intestine.",
      "Blue water drops soak up in the large intestine. The rest is waste."] },
  thu: { tab: "Thu · Clean-Up", color: "#c2410c", title: "Thursday · The Clean-Up Crew", organs: ["liver", "kidneys", "bladder"],
    rudy: "Cells make trash. The liver and kidneys clean my river so it stays safe!",
    watch: ["Gray waste goes into the kidneys and comes out as yellow urine.",
      "Watch the bladder fill up like a balloon.",
      "Green sparkles: the liver making harmful stuff safe.",
      "Tap Drink water: more water makes paler pee!"] },
  fri: { tab: "Fri · Brain", color: "#0f766e", title: "Friday · The Head Coach", organs: ["brain", "nerves", "senses"],
    rudy: "My favorite stop! The brain uses about a fifth of all the oxygen I carry.",
    watch: ["Yellow flashes are messages zipping along the nerves.",
      "Messages come IN from your eyes and ears, and go OUT to your muscles.",
      "Play the Ruler Drop below: how fast is YOUR brain?"] },
  team: { tab: "Whole Team", color: "#b91c1c", title: "The Whole Body Team", organs: [],
    rudy: "That's my whole route: lungs, heart, out to the body, and back again, about once a minute!",
    watch: ["Tap any organ to learn its job.", "Tap Follow Rudy and ride along!",
      "Tap Sprint to see the whole team speed up at once."] },
};
const DAY_KEYS = ["mon", "tue", "wed", "thu", "fri", "team"];

const state = { day: "team", sprint: false, follow: false, labels: true, bpm: 90, brpm: 20,
  beat: 0, breath: 0, hydration: 0.35, bladder: 0.25, sceneT: 0, acc: {} };

// ---------- Camera: pan / zoom / fly ----------
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
  const pad = 36;
  const s = clampS(Math.min(600 / (b.width + 2 * pad), 1000 / (b.height + 2 * pad)));
  const sf = s * 0.9;
  return { s: sf, x: 300 - sf * (b.x + b.width / 2), y: 525 - sf * (b.y + b.height / 2) };
}
function organBox(names) {
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  names.forEach((n) => {
    const b = document.querySelector(`[data-organ="${n}"]`).getBBox();
    x0 = Math.min(x0, b.x); y0 = Math.min(y0, b.y); x1 = Math.max(x1, b.x + b.width); y1 = Math.max(y1, b.y + b.height);
  });
  return { x: x0, y: y0, width: x1 - x0, height: y1 - y0 };
}
const WHOLE = { s: 0.9, x: 30, y: 72 };

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
$("zoomIn").onclick = () => { camAnim = null; zoomAt(300, 500, 1.3); };
$("zoomOut").onclick = () => { camAnim = null; zoomAt(300, 500, 1 / 1.3); };
$("zoomReset").onclick = () => { setFollow(false); flyTo(WHOLE); };

// ---------- UI ----------
let toastTimer = null;
function toast(msg) {
  const t = $("toast"); t.textContent = msg; t.classList.add("show");
  clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.remove("show"), 2200);
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
$("followBtn").onclick = () => { setFollow(!state.follow); if (!state.follow) flyTo(dayView()); };
$("sprintBtn").onclick = () => {
  state.sprint = !state.sprint;
  $("sprintBtn").classList.toggle("on", state.sprint); $("sprintBtn").setAttribute("aria-pressed", state.sprint);
  $("sprintBtn").textContent = state.sprint ? "🛋️ Rest" : "🏃 Sprint!";
  toast(state.sprint ? "Sprinting! Heart and lungs speed up together." : "Resting. Everything slows back down.");
};
$("labelsBtn").onclick = () => {
  state.labels = !state.labels;
  $("labelsBtn").classList.toggle("on", state.labels); $("labelsBtn").setAttribute("aria-pressed", state.labels);
  updateLabels();
};

DAY_KEYS.forEach((k, i) => {
  const b = document.createElement("button");
  b.textContent = DAYS[k].tab; b.style.background = DAYS[k].color; b.dataset.day = k;
  b.title = `Key ${i + 1}`; b.onclick = () => selectDay(k);
  $("days").appendChild(b);
});

for (const [key, o] of Object.entries(ORGANS)) {
  if (!o.at) continue;
  const t = document.createElementNS(NS, "text");
  t.setAttribute("class", "label"); t.setAttribute("x", o.at[0]); t.setAttribute("y", o.at[1]);
  t.setAttribute("text-anchor", o.anchor || "middle"); t.dataset.for = key; t.textContent = o.name;
  $("labels").appendChild(t);
}
function updateLabels() {
  const focus = DAYS[state.day].organs;
  document.querySelectorAll("#labels text").forEach((t) => {
    const show = state.labels && (state.day === "team" || focus.includes(t.dataset.for));
    t.setAttribute("opacity", show ? 1 : 0);
  });
}
function dayView() {
  const d = DAYS[state.day];
  const f = d.fit || d.organs;
  return f.length ? fitBox(organBox(f)) : WHOLE;
}

function selectDay(key) {
  state.day = key; state.sceneT = 0; state.acc = {};
  const d = DAYS[key];
  document.documentElement.style.setProperty("--accent", d.color);
  document.querySelectorAll("#days button").forEach((b) => b.setAttribute("aria-pressed", b.dataset.day === key));
  document.querySelectorAll(".organ").forEach((g) => {
    g.classList.toggle("dim", d.organs.length > 0 && !d.organs.includes(g.dataset.organ));
  });
  $("dayTitle").textContent = d.title;
  $("rudySays").textContent = d.rudy;
  $("watch").innerHTML = d.watch.map((w) => `<li>${w}</li>`).join("");
  $("legend").style.display = ["mon", "tue", "team"].includes(key) ? "" : "none";
  cellsLayer.setAttribute("opacity", ["mon", "tue", "team"].includes(key) ? 1 : 0.35);
  $("breathText").setAttribute("opacity", 0);
  clearParticles(); bolus.setAttribute("opacity", 0);
  buildExtra(key); updateLabels();
  setFollow(false); flyTo(dayView());
  if (location.hash !== "#" + key) history.replaceState(null, "", "#" + key);
}

// ---------- Particles ----------
const parts = [];
function spawn(o) {
  const c = document.createElementNS(NS, "circle");
  c.setAttribute("r", o.r || 4); c.setAttribute("fill", o.color || "#fff");
  if (o.glow) c.setAttribute("filter", "url(#glow)");
  fx.appendChild(c);
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

// ---------- Blood cells and Rudy on the loop ----------
const loop = $("loopPath"), LOOP_LEN = loop.getTotalLength();
function nearestLen(x, y, from = 0) {
  let best = from, bd = Infinity;
  for (let l = from; l <= LOOP_LEN; l += 2) {
    const p = loop.getPointAtLength(l); const d = (p.x - x) ** 2 + (p.y - y) ** 2;
    if (d < bd) { bd = d; best = l; }
  }
  return best / LOOP_LEN;
}
const F_LUNG = nearestLen(240, 360), F_BRAIN = nearestLen(304, 122);
const F_HEART2 = nearestLen(318, 410, F_BRAIN * LOOP_LEN), F_LEG = nearestLen(245, 952, F_HEART2 * LOOP_LEN);
const oxygenated = (f) => (f > F_LUNG && f < F_BRAIN) || (f > F_HEART2 && f < F_LEG);

const N_CELLS = 22, cells = [];
for (let i = 0; i < N_CELLS; i++) {
  if (i === 0) {
    const g = document.createElementNS(NS, "g"); g.dataset.organ = "rudy"; g.style.cursor = "pointer";
    g.innerHTML = '<circle r="11" class="body" stroke="#450a0a" stroke-width="1.5"/>' +
      '<circle cx="-4" cy="-3" r="2.6" fill="#fff"/><circle cx="4" cy="-3" r="2.6" fill="#fff"/>' +
      '<circle cx="-4" cy="-3" r="1.2" fill="#111"/><circle cx="4" cy="-3" r="1.2" fill="#111"/>' +
      '<path d="M -4 4 Q 0 7.5 4 4" fill="none" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/>';
    cellsLayer.appendChild(g); cells.push({ el: g, off: 0, rudy: true });
  } else {
    const c = document.createElementNS(NS, "circle"); c.setAttribute("r", 5);
    c.setAttribute("stroke", "#450a0a"); c.setAttribute("stroke-width", 1); c.style.pointerEvents = "none";
    cellsLayer.appendChild(c); cells.push({ el: c, off: i / N_CELLS });
  }
}
let loopPos = 0, rudyXY = [322, 415];
function updateBlood(dt) {
  loopPos = (loopPos + dt * (state.bpm / 90) / 16) % 1;
  for (const c of cells) {
    const f = (loopPos + c.off) % 1;
    const p = loop.getPointAtLength(f * LOOP_LEN);
    const col = oxygenated(f) ? "#ef4444" : "#7f1d1d";
    if (c.rudy) {
      c.el.setAttribute("transform", `translate(${p.x.toFixed(1)} ${p.y.toFixed(1)})`);
      c.el.querySelector(".body").setAttribute("fill", col); rudyXY = [p.x, p.y];
    } else {
      c.el.setAttribute("cx", p.x.toFixed(1)); c.el.setAttribute("cy", p.y.toFixed(1)); c.el.setAttribute("fill", col);
    }
  }
}

// ---------- Heart and breathing (always running) ----------
let lubDubShown = 0;
function onBeat() {
  if (state.day !== "tue") return;
  const t = document.createElementNS(NS, "text");
  t.setAttribute("class", "worldtext"); t.setAttribute("x", 372); t.setAttribute("y", 392);
  t.style.fontSize = "18px"; t.textContent = lubDubShown++ % 2 ? "dub!" : "lub-dub!";
  fx.appendChild(t); setTimeout(() => t.remove(), 450);
}
function animateBody() {
  const b = state.beat, squeeze = b < 0.2 ? Math.sin((b / 0.2) * Math.PI) : 0;
  $("heartInner").setAttribute("transform", `translate(322 415) rotate(-35) scale(${(1.45 * (1 - 0.09 * squeeze)).toFixed(3)})`);
  const inh = 0.5 - 0.5 * Math.cos(2 * Math.PI * state.breath);
  $("lungsInner").setAttribute("transform",
    `translate(300 300) scale(${(1 + 0.045 * inh).toFixed(3)} ${(1 + 0.075 * inh).toFixed(3)}) translate(-300 -300)`);
  $("diaphragmPath").setAttribute("d", `M 195 ${(482 + 10 * inh).toFixed(1)} Q 300 ${(430 + 34 * inh).toFixed(1)} 405 ${(482 + 10 * inh).toFixed(1)}`);
  return inh;
}

// ---------- Day scenes ----------
const bolus = document.createElementNS(NS, "circle");
bolus.setAttribute("r", 9); bolus.setAttribute("stroke", "#451a03"); bolus.setAttribute("stroke-width", 1.5);
bolus.setAttribute("opacity", 0); $("world").insertBefore(bolus, cellsLayer);
const PATHS = Object.fromEntries(["esoPath", "smallPath", "largePath", "airL", "airR", "renalL", "renalR",
  "ureterL", "ureterR", "portalPath", "eyePath", "earPath", "handPath", "legPath"].map((id) => [id, $(id)]));
const lenOf = Object.fromEntries(Object.entries(PATHS).map(([k, p]) => [k, p.getTotalLength()]));
const at = (id, k) => PATHS[id].getPointAtLength(Math.max(0, Math.min(1, k)) * lenOf[id]);

function sceneMon(dt) {
  const inhaling = state.breath < 0.5;
  const txt = $("breathText");
  txt.textContent = inhaling ? "Breathe in!" : "Breathe out!";
  txt.setAttribute("opacity", 1);
  const rate = 0.12 * (20 / state.brpm);
  every("air", rate, dt, () => {
    const side = Math.random() < 0.5 ? "airL" : "airR";
    if (inhaling) spawn({ path: PATHS[side], dur: 1.1 * (20 / state.brpm) * 1.6, r: 4, color: "#7dd3fc", fade: false });
    else spawn({ path: PATHS[side], rev: true, dur: 1.1 * (20 / state.brpm) * 1.6, r: 4, color: "#94a3b8" });
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
  const fill = Math.min(1, state.bladder);
  const h = 36 * fill;
  const bf = $("bladderFill");
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
  spawn({ path: PATHS[inPath], dur: 0.35, r: 5, color: "#fde047", glow: true, then: () => {
    brainFlash();
    spawn({ path: PATHS[outPath], dur: 0.6, r: 5, color: "#fde047", glow: true });
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
      '<div class="legend">Water in your body:</div><div class="meter"><div id="hydroMeter"></div></div>' +
      '<div class="legend">Pale yellow pee = plenty of water. Dark yellow = drink up!</div>';
    $("drinkBtn").onclick = () => { state.hydration = Math.min(1, state.hydration + 0.35); toast("Glug, glug! 💧 The kidneys have more water to wash waste away."); };
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
function renderTries() {
  const el = $("tries"); if (!el) return;
  el.innerHTML = game.tries.map((t) => `<li>${t}</li>`).join("");
}
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
  else if (e.key === "+" || e.key === "=") zoomAt(300, 500, 1.25);
  else if (e.key === "-") zoomAt(300, 500, 0.8);
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
    const s = 3, tx = 300 - s * rudyXY[0], ty = 500 - s * rudyXY[1], k = Math.min(1, dt * 4);
    cam.s += (s - cam.s) * k; cam.x += (tx - cam.x) * k; cam.y += (ty - cam.y) * k; applyCam();
  } else if (camAnim) {
    const j = Math.min(1, (now - camAnim.t0) / camAnim.ms), e = j < 0.5 ? 2 * j * j : 1 - (-2 * j + 2) ** 2 / 2;
    for (const key of ["x", "y", "s"]) cam[key] = camAnim.from[key] + (camAnim.to[key] - camAnim.from[key]) * e;
    applyCam(); if (j >= 1) camAnim = null;
  }
  $("readout").textContent = `♥ ${Math.round(state.bpm)} beats/min · 🫁 ${Math.round(state.brpm)} breaths/min`;
  requestAnimationFrame(frame);
}

applyCam();
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
