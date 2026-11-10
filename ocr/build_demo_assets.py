"""Build real-file edit examples with Verovio; never overwrite the source OMR.

pip install playwright
python ocr/build_demo_assets.py

The before/after files differ in ONE pitch (F4 -> G4). The repair example
adds the missing final F4 only; it is an illustration, not a pipeline result.
"""
import copy
import json
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from urllib.request import urlopen
from playwright.sync_api import sync_playwright
from render_bars import clip, OMR, VOICE

OUT = Path(__file__).resolve().parent.parent / 'img'


def svg(xml, name, highlight):
    rendered = page.evaluate('''xml => {
      const tk = new verovio.toolkit(); tk.resetXmlIdSeed(7);
      tk.setOptions({pageWidth:1400,pageHeight:400,scale:60,adjustPageHeight:true,
        breaks:'none',header:'none',footer:'none',spacingLinear:.3});
      if (!tk.loadData(xml)) throw new Error('MusicXML load failed');
      return tk.renderToSVG(1);
    }''', xml)
    root = ET.fromstring(rendered)
    ns = {'s': 'http://www.w3.org/2000/svg'}
    notes = [e for e in root.iter() if e.get('class') == 'note']
    assert len(notes) in (6, 7)
    if highlight is not None:
        notes[highlight].set('color', '#2563a8')
        notes[highlight].set('fill', '#2563a8')
        notes[highlight].set('stroke', '#2563a8')
    # Verovio emits an outer pixel viewport and an inner music viewBox.
    # Preserve that geometry and all music glyphs; the browser scales the SVG.
    ET.register_namespace('', ns['s'])
    ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
    (OUT / f'ocr_{name}.svg').write_text(ET.tostring(root, encoding='unicode'), encoding='utf-8')
    (OUT / f'ocr_{name}.musicxml').write_text(xml, encoding='utf-8')


with tempfile.TemporaryDirectory() as folder, sync_playwright() as pw:
    browser = pw.chromium.launch(channel='chrome')
    page = browser.new_page()
    # Build-time dependency only; the public page ships the generated SVGs.
    cache = Path(tempfile.gettempdir()) / 'portfolio-verovio-6.0.0.js'
    if not cache.exists():
        with urlopen('https://www.verovio.org/javascript/6.0.0/verovio-toolkit-wasm.js', timeout=60) as response:
            cache.write_bytes(response.read())
    page.add_script_tag(path=str(cache))
    page.evaluate('''() => new Promise(resolve => {
      if (verovio.module.calledRun) resolve();
      else verovio.module.onRuntimeInitialized = resolve;
    })''')
    version = page.evaluate('new verovio.toolkit().getVersion()')
    raw = Path(folder) / 'raw.xml'
    with zipfile.ZipFile(OMR) as archive:
        raw.write_bytes(archive.read('hab_test.xml'))
    cut = Path(folder) / 'cut.musicxml'
    clip(raw, [6], cut, {VOICE})
    root = ET.parse(cut).getroot()
    # Drop absolute engraving coordinates, not musical content.
    for e in root.iter():
        for key in list(e.attrib):
            if key in ('default-x', 'default-y', 'relative-x', 'relative-y', 'width') or key.startswith('bezier-'):
                del e.attrib[key]
    measure = root.find('part/measure')
    notes = measure.findall('note')
    assert [n.findtext('pitch/step') for n in notes] == ['F', 'G', 'F', 'E', 'F', 'G']
    before = ET.tostring(root, encoding='unicode')
    svg(before, 'edit_before', 0)
    notes[0].find('pitch/step').text = 'G'
    after = ET.tostring(root, encoding='unicode')
    assert after == before.replace('<step>F</step>', '<step>G</step>', 1)
    svg(after, 'edit_after', 0)
    notes[0].find('pitch/step').text = 'F'
    added = ET.fromstring('<note><pitch><step>F</step><octave>4</octave></pitch><duration>2</duration><voice>1</voice><type>eighth</type><stem>up</stem></note>')
    measure.append(added)
    svg(ET.tostring(root, encoding='unicode'), 'repair_example', -1)
    browser.close()

(OUT / 'ocr_edit_manifest.json').write_text(json.dumps({
    'source': 'ocr/habanera_omr.mxl', 'part': VOICE, 'measure': 7,
    'before_midi': 65, 'after_midi': 67, 'renderer': version,
    'edit': 'First note F4 to G4; all other musical content unchanged.',
    'repair': 'Missing final F4 added manually for illustration; other recognition errors remain.'
}, ensure_ascii=False, indent=2), encoding='utf-8')
print('Built two real MusicXML edit states and a labelled repair illustration.')
